import json
import re
import subprocess
import sys
from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand, CommandError
from git import GitCommandError
from git import Repo


class Command(BaseCommand):
    help = 'This command will install specified module locally'
    _default_branch = 'develop'

    def __init__(self):
        super().__init__()
        self.path = Path(settings.BASE_DIR)
        self.openimis_json = None
        self.installed_modules = None

    def add_arguments(self, parser):
        parser.add_argument(
            'module_name',
            type=str,
            help='Set the module to be installed locally. Use "all" to install all modules present in openimis.json. Fetching all modules does not support --url.'
        )

        parser.add_argument(
            '-u', '--url',
            type=str,
            help='Set the url to the module repository. If not specified, url from openimis.json will be used.',
        )

        parser.add_argument(
            '-b', '--branch',
            type=str,
            help='Set the repository branch to use. If not specified, develop will be used.',
        )

        parser.add_argument(
            '-p', '--path',
            type=str,
            help='Set the path that will be used to clone the repository and install the module. If not specified, repository will be saved next to openimis-be_py and installed using the absolute path.',
        )

    def handle(self, *args, **options):
        with self.path.parent.joinpath('openimis.json').open("r") as file:
            self.openimis_json = json.load(file)
        self.installed_modules = [module['name'] for module in self.openimis_json['modules']]

        module = options['module_name']
        if module.lower() == 'all':
            if options['url']:
                raise CommandError("Fetching all modules does not support --url")
            for module_to_fetch in self.installed_modules:
                try:
                    self._handle_fetch_single_module(module_to_fetch, **options)
                except CommandError as e:
                    self.stderr.write(f'{module_to_fetch}: {e}')
        else:
            self._handle_fetch_single_module(module, **options)

        with self.path.parent.joinpath('openimis.json').open("w") as file:
            json.dump(self.openimis_json, file, indent=2)

    def _handle_fetch_single_module(self, module, **options):
        url = self._get_target_url(module, **options)

        if url.lower().startswith("-e"):
            self._print_info(f'"{module}" url points to local directory, skipping')
            return

        directory = self._get_target_directory(module, **options)
        if directory.exists():
            raise CommandError(f'"{directory}" already exist. Module "{module}" cannot be installed')

        branch = self._get_target_branch(**options)

        self._print_info(f'Fetching module "{module}" from "{url}"')
        self._fetch_from_url(url, directory, branch)
        self._install_module_locally(f'openimis-be-{module}', directory)

        if module in self.installed_modules:
            self._update_module_path(module, directory)
        else:
            self._add_module_path(module, directory)

    def _get_target_directory(self, module, **options):
        directory = options['path']
        module_dir = f'openimis-be-{module}_py'
        if directory:
            return Path(directory).joinpath(module_dir)
        else:
            return self.path.parent.parent.joinpath(module_dir)

    def _get_target_branch(self, **options):
        branch = options['branch']
        if not branch:
            branch = self._default_branch
        return branch

    def _get_target_url(self, module, **options):
        url = options['url']
        if not url:
            url = self.get_url_from_openimis_json(module)
        return url

    def get_url_from_openimis_json(self, module):
        module_pip_path = [module_entry['pip'] for module_entry in self.openimis_json['modules'] if module_entry['name'] == module]

        if module_pip_path:
            module_pip_path = module_pip_path[0]
        else:
            raise CommandError(f'"{module}" module does not contain pip path in "openimis.json". Please fix the "openimis.json" file.')

        if module_pip_path.lower().startswith("-e"):
            return module_pip_path

        module_url = self.extract_clone_url_from_pip_path(module_pip_path)
        if module_url:
            return module_url
        else:
            raise CommandError(f'"{module}" module does not contain valid/supported git url in "openimis.json". Please make sure pip path in "openimis.json" contains repository url (ending with ".git").')

    def extract_clone_url_from_pip_path(self, pip_path):
        # currently this only supports https cloning, adding ssh cloning is possible
        matched_url = re.search(r'^git\+(https.+\.git)', pip_path)
        if matched_url:
            return matched_url.group(1)

    def _fetch_from_url(self, url, directory, branch):
        try:
            Repo.clone_from(url, directory, branch=branch)
            self._print_info(f'Repository fetched to "{directory}"')
        except GitCommandError as e:
            raise CommandError(f'Fetching repository failed:\n{str(e)}')

    def _install_module_locally(self, module_library, directory):
        self._print_info(f'Removing installed version of "{module_library}"')
        subprocess.check_call([sys.executable, '-m', 'pip', 'uninstall', module_library, '-y'], stdout=subprocess.DEVNULL)
        self._print_info(f'Installing "{module_library}" from "{directory}"')
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-e', str(directory)], stdout=subprocess.DEVNULL)

    def _update_module_path(self, module, directory):
        for module_entry in self.openimis_json['modules']:
            if module_entry['name'] == module:
                module_entry['pip'] = f'-e {directory}'
                break

    def _add_module_path(self, module, directory):
        self.openimis_json['modules'].append({"name": module, "pip": f'-e {directory}'})

    def _print_info(self, message):
        self.stdout.write(message)

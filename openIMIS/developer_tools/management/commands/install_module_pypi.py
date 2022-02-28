import json
import subprocess
import sys
from pathlib import Path

import requests
from django.conf import settings
from django.core.management import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'This command will help installing modules from PyPI'
    _metadata_path = 'https://pypi.org/pypi/{library_name}/json'

    def __init__(self):
        super().__init__()
        self.path = Path(settings.BASE_DIR)
        self.openimis_json = None
        self.installed_modules = None

    def add_arguments(self, parser):
        parser.add_argument(
            'module_name',
            type=str,
            help='Set the module to be installed from pypi. Use "all" to install all modules present in openimis.json.'
        )

        parser.add_argument(
            '-t', '--target-version',
            type=str,
            help='Set the version of the module to be used. By default the newest version is chosen.',
        )

        parser.add_argument(
            '-l', '--library-name',
            type=str,
            help='Override the library name, "openimis-be-<module_name>" is used by default.\n'
                 'Not supported for all modules mode.',
        )

        parser.add_argument(
            '-c', '--check-only',
            nargs='?',
            const=True,
            help='Set the command to only check the most recent version of the module. This switch supress any changes to the project structure. Use together with --target-version to check if that version is available.',
        )

    def handle(self, *args, **options):
        self._validate_arguments(**options)

        with self.path.parent.joinpath('openimis.json').open("r") as file:
            self.openimis_json = json.load(file)
        self.installed_modules = [module['name'] for module in self.openimis_json['modules']]

        module = options['module_name']
        if module.lower() == 'all':
            for module_to_install in self.installed_modules:
                try:
                    self._handle_single_module(module_to_install, **options)
                except Exception as e:
                    self.stderr.write(f'{module_to_install}: {e}')
        else:
            self._handle_single_module(module, **options)

        with self.path.parent.joinpath('openimis.json').open("w") as file:
            json.dump(self.openimis_json, file, indent=2)

    def _validate_arguments(self, **options):
        if options['module_name'].lower() == 'all' and options['library_name']:
            raise CommandError("Installing all modules does not support --library-name.")

    def _handle_single_module(self, module, **options):
        module_library = self._get_lib_name(module, **options)
        lib_metadata = self._fetch_metadata(module, module_library)
        version = self._get_version(lib_metadata, options['target_version'])
        if not options['check_only']:
            self._install_module(module_library, version)
            self._update_openimis_json(module, module_library, version)
            self._print_success(f'Module "{module}" installed successfully.')
        else:
            if options['target_version']:
                self._print_success(f'"{module_library}" version "{version}" is available.')
            else:
                self._print_success(f'"The most recent version available for {module_library}" is "{version}".')

    def _get_lib_name(self, module, **options):
        lib_name = options['library_name']
        if not lib_name:
            lib_name = f'openimis-be-{module}'
        return lib_name

    def _fetch_metadata(self, module, module_library):
        self._print_info(f'Fetching metadata for "{module}" ({module_library})')
        response = requests.get(self._metadata_path.format(**{'library_name': module_library}))
        if response.status_code != 200:
            raise CommandError(
                f'Error while fetching "{module_library}" metadata: {response.status_code} {response.reason}\n'
                'Please try --library-name argument if the library name does not match the default scheme.')
        return response.json()

    def _get_version(self, lib_metadata, target_version=None):
        if not target_version:
            # pick last release version
            return lib_metadata["info"]['version']

        # check if target version is available
        matching_versions = [release_version for release_version in lib_metadata['releases']
                             if release_version == target_version]
        if not matching_versions:
            raise CommandError(f'"{target_version}" of "{lib_metadata["info"]["name"]}" is not available')
        else:
            return matching_versions[0]

    def _install_module(self, module_library, version):
        self._print_info(f'Removing installed version of "{module_library}".')
        subprocess.check_call([sys.executable, '-m', 'pip', 'uninstall', module_library, '-y'],
                              stdout=subprocess.DEVNULL)
        self._print_info(f'Installing "{module_library}" version "{version}".')
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', f'{module_library}=={version}'],
                              stdout=subprocess.DEVNULL)

    def _update_openimis_json(self, module, module_library, version):
        if module in self.installed_modules:
            self._update_module_path(module, module_library, version)
        else:
            self._add_module_path(module, module_library, version)

    def _update_module_path(self, module, module_library, version):
        for module_entry in self.openimis_json['modules']:
            if module_entry['name'] == module:
                module_entry['pip'] = f'{module_library}=={version}'
                break

    def _add_module_path(self, module, module_library, version):
        self.openimis_json['modules'].append({"name": module, "pip": f'{module_library}=={version}'})

    def _print_success(self, message):
        self.stdout.write(message, self.style.SUCCESS)

    def _print_info(self, message):
        self.stdout.write(message)

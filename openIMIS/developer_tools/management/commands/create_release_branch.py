import git
import json

from django.conf import settings
from django.core.management.base import BaseCommand
from pathlib import Path

from openIMIS.openimisapps import openimis_apps


class Command(BaseCommand):
    help = "This command will generate release branches in one command"

    def add_arguments(self, parser):
        parser.add_argument('release_tag', type=str)
        parser.add_argument('from_brach', type=str, default='develop')

    def handle(self, *args, **options):
        release_tag = options['release_tag']
        from_brach = options['from_brach']
        self.__print_info(f'starting creating release branches for backend')
        output = self.create_release_branches_backend(release_tag, from_brach)
        self.__print_success('Creating release branches finished for backend modules')
        self.__print_info(f'{output}')
        self.__print_info(f'starting creating release branches for frontend')
        output = self.create_release_branches_frontend(release_tag, from_brach)
        self.__print_success('Creating release branches finished for frontend modules')
        self.__print_info(f'{output}')

    def create_release_branches_backend(self, version, from_branch):
        """
            function to create release branches 'release/<version>'
            for all backend modules presented in openimis.json
        """
        output_messages = []
        modules = openimis_apps()
        release_branch = f'release/{version}'
        base_path = Path(settings.BASE_DIR)
        modules_directory = base_path.parent.parent
        for module in modules:
            try:
                repo_name = f"openimis-be-{module}_py"
                module_directory = Path(modules_directory).joinpath(repo_name)
                self.__check_module_exist_locally(module_directory.joinpath(module), module, 'be')
                self.__do_git_operations(module_directory, from_branch, release_branch)
                output_messages.append({
                    'module': module,
                    'message': f'Operation succeded'
                })
            except Exception as exc:
                output_messages.append({
                    'module': module,
                    'message': f'Operation failed: {exc}'
                })
        return output_messages

    def create_release_branches_frontend(self, version, from_branch):
        """
           function to create release branches 'release/<version>'
           for all frontend modules presented in openimis.json
        """
        output_messages = []
        # check if main frontend module is presented locally.
        base_path = Path(settings.BASE_DIR)
        modules_directory = base_path.parent.parent
        if not Path(modules_directory).joinpath('openimis-fe_js').exists():
            raise Exception("Main assembly frontend module not presented locally")

        # take the module names from fe openimis.json
        modules = self.__read_frontend_openimis_file(modules_directory)
        release_branch = f'release/{version}'
        for module in modules:
            try:
                repo_name = f"openimis-{module}_js"
                module_directory = Path(modules_directory).joinpath(repo_name)
                self.__check_module_exist_locally(module_directory, module.split('-')[1], 'fe')
                self.__do_git_operations(module_directory, from_branch, release_branch)
                output_messages.append({
                    'module': module,
                    'message': f'Operation succeded'
                })
            except Exception as exc:
                output_messages.append({
                    'module': module,
                    'message': f'Operation failed: {exc}'
                })
        return output_messages

    def __do_git_operations(self, module_directory, from_branch, release_branch):
        local_repo = git.Repo(module_directory)
        current_branch = local_repo.active_branch
        if current_branch != from_branch:
            local_repo.git.checkout(from_branch)
        # create release branch if not exist in local repo
        if release_branch not in local_repo.branches:
            local_repo.git.branch(release_branch)
        local_repo.git.checkout(release_branch)
        # pull changes from develop/particular branch
        local_repo.git.pull("origin", from_branch)
        # push branch to remote branch
        local_repo.git.push("origin", release_branch)
        # back to branch previously assigned
        local_repo.git.checkout(current_branch)

    def __read_frontend_openimis_file(self, modules_directory):
        # take the module names from fe openimis.json
        modules = []
        openimis_json = Path(modules_directory).joinpath('openimis-fe_js').joinpath('openimis.json')
        with open(openimis_json) as json_file:
            json_data = json.load(json_file)
            for module in json_data['modules']:
                module_name = module['npm'].split('/')[1].split('@')[0]
                modules.append(module_name)
        return modules

    def __check_module_exist_locally(self, module_directory, module, module_type):
        # check if frontend module exists locally
        extension = 'py' if module_type == 'be' else 'js'
        if not Path(module_directory).exists():
            git.Repo.clone_from(
                f'https://github.com/openimis/openimis-{module_type}-{module}_{extension}.git',
                module_directory
            )

    def __print_success(self, msg: str):
        """ Print message to inform about the command progress """
        self.stdout.write(self.style.SUCCESS(msg))

    def __print_info(self, msg: str):
        """ Print message to inform about the command progress = info """
        self.stdout.write(self.style.WARNING(msg))

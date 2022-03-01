import os
import json

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from git import Repo
from pathlib import Path

class Command(BaseCommand):
    help = "This command will generate backend module skeleton in one command"

    supported_templates = ('business', 'calculation')

    def add_arguments(self, parser):
        parser.add_argument('module_name', type=str)
        parser.add_argument('author', type=str)
        parser.add_argument('author_email', type=str)

        parser.add_argument(
            '-t', '--template',
            nargs='?',
            help=f'Select a template to be used when creating new module. Supported templates are: {", ".join(self.supported_templates)}',
        )
        parser.add_argument(
            '--github',
            action='store_true',
            help='Add github files related to workflow and .gitignore',
        )

    def handle(self, *args, **options):
        # get basic data to create new module like module name, current path/directory
        author = options['author']
        author_email = options['author_email']
        module_name = options['module_name']
        template = options['template']
        if template and template not in self.supported_templates:
            raise CommandError(f'template "{template}" is not supported. Chech --help for the list of supported templates')

        if options['template'] == 'calculation':
            self.__call_add_calcrule_module_command(module_name, author, author_email, options['github'])
        else:
            repo_name = f"openimis-be-{module_name}_py"
            base_path = Path(settings.BASE_DIR)
            modules_directory = base_path.parent.parent

            new_module_directory = Path(modules_directory).joinpath(repo_name)

            # check if module exists locally
            if Path(new_module_directory).joinpath(module_name).exists():
                raise CommandError("Module already exists in workspace")

            app_directory = self.__create_project_folder(module_name, new_module_directory)
            self.__print_info(str(app_directory))

            Repo.init(new_module_directory)

            self.__create_skeleton_module(module_name, app_directory)

            skeletons_folder = Path(base_path).joinpath('developer_tools').joinpath('skeletons')

            self.__add_setup_file(skeletons_folder, new_module_directory, module_name, author, author_email)
            self.__add_readme_file(skeletons_folder, new_module_directory, module_name)
            self.__add_license_file(skeletons_folder, new_module_directory)
            self.__add_manifest_file(skeletons_folder, new_module_directory)
            self.__add_urls_file(skeletons_folder, app_directory)

            self.__install_module(module_name, new_module_directory)
            self.__add_module_to_openimis_json(base_path, module_name)

            if options['template'] == 'business':
                self.__add_business_services_file(skeletons_folder, app_directory)
                self.__add_business_tests_file(skeletons_folder, app_directory, module_name)

            self.__call_tests(module_name)

            if options['github']:
                self.__call_add_github_files_command(module_name)

    def __create_project_folder(self, module_name, new_module_directory):
        """ create empty folder for new project """
        try:
            new_module_directory.mkdir()
            app_directory = new_module_directory.joinpath(module_name)
            app_directory.mkdir()
        except Exception as exc:
            raise CommandError(f"Creation of the directory failed, reason: {exc}")
        else:
            self.__print_success(f"Successfully created the directory {app_directory}")
            return app_directory

    def __create_skeleton_module(self, module_name, app_directory):
        result = os.system(f'python manage.py startapp {module_name} {app_directory}')
        if result != 0:
            raise CommandError(f'Skeleton module not created properly, ended with code: {result}')
        else:
            self.__print_success('Succesfully created skeleton module')

    def __add_readme_file(self, skeletons_folder, new_module_directory, module_name):
        file_content = self.__replace_skeleton_values(skeletons_folder, 'README.md', module_name=module_name)
        self.__add_file(new_module_directory, 'README.md', file_content)

    def __add_license_file(self, skeletons_folder, new_module_directory):
        file_content = self.__replace_skeleton_values(skeletons_folder, 'LICENSE.md')
        self.__add_file(new_module_directory, 'LICENSE.md', file_content)

    def __add_manifest_file(self, skeletons_folder, new_module_directory):
        file_content = self.__replace_skeleton_values(skeletons_folder, 'MANIFEST.md')
        self.__add_file(new_module_directory, 'MANIFEST.md', file_content)

    def __add_urls_file(self, skeletons_folder, app_directory):
        file_content = self.__replace_skeleton_values(skeletons_folder, 'urls.py')
        self.__add_file(app_directory, 'urls.py', file_content)

    def __add_business_services_file(self, skeletons_folder, app_directory):
        file_content = self.__replace_skeleton_values(skeletons_folder, 'business_services.template')
        self.__add_file(app_directory, 'services.py', file_content)

    def __add_business_tests_file(self, skeletons_folder, app_directory, module_name):
        file_content = self.__replace_skeleton_values(skeletons_folder, 'business_tests.template', module_name=module_name)
        self.__add_file(app_directory, 'tests.py', file_content)

    def __add_business_apps_file(self, skeletons_folder, app_directory, module_name):
        file_content = self.__replace_skeleton_values(skeletons_folder, 'business_apps.template', module_name=module_name)
        self.__add_file(app_directory, 'apps.py', file_content)

    def __add_setup_file(self, skeletons_folder, new_module_directory, module_name, author, author_email):
        file_content = self.__replace_skeleton_values(
            skeletons_folder, 'setup.py',
            module_name=module_name, author=author, author_email=author_email
        )
        self.__add_file(new_module_directory, 'setup.py', file_content)

    def __install_module(self, module_name, new_module_directory):
        """ Install newly created module in workspace """
        result = os.system(f'pip install -e {Path(f"{new_module_directory}/")}')
        if result != 0:
            raise CommandError(f'Failed during installation of module {module_name}')
        else:
            self.__print_success(f'Succesfully installed module {module_name}')

    def __add_module_to_openimis_json(self, base_path, module_name):
        """ Add to the openimis.json newly created module """
        module_to_append = {
            "name": f"{module_name}",
            "pip": f"-e ../../openimis-be-{module_name}_py",
        }
        openimis_json_location = base_path.parent
        with open(openimis_json_location.joinpath('openimis.json'), "r") as read_file:
            openimis_json = json.load(read_file)

        if "modules" in openimis_json:
            openimis_json["modules"].append(module_to_append)
            with open(openimis_json_location.joinpath('openimis.json'), "w") as file:
                json.dump(openimis_json, file, indent=4)
                self.__print_success('Succesfully updated openimis.json')
        else:
            raise CommandError("Error: there is no 'modules' keyword in existing openimis.json file")

    def __replace_skeleton_values(self, skeletons_folder, file_name, **kwargs):
        """
            Take the skeleton for chosen file and replace values.
            Returns transformed content of file.
        """
        with open(skeletons_folder.joinpath(file_name), 'r') as file:
            file_text = file.read()
        for key, value in kwargs.items():
            if "{{"+key+"}}" in file_text:
                file_text = file_text.replace("{{"+key+"}}", value)
        return file_text

    def __add_file(self, new_module_directory, filename, file_content):
        """ Add file to the project of new module """
        file = new_module_directory.joinpath(filename)
        self.__print_info(str(file))
        with open(file, "w+") as f:
            f.write(file_content)
        self.__print_success(f'Succesfully created {filename} file')

    def __call_add_github_files_command(self, module_name):
        result = os.system(f"python manage.py add_github_files_to_module '{module_name}'")
        if result != 0:
            raise CommandError(f'Error on adding GitHub files to the module')
        else:
            self.__print_success('Successfully added GitHub files to the module')

    def __call_tests(self, module_name):
        self.__print_info("Running example tests")
        result = os.system(f"python manage.py test {module_name} --keep")
        if result != 0:
            raise CommandError(f'Error while running example tests')
        else:
            self.__print_success('Successfully completed example tests')

    def __call_add_calcrule_module_command(self, module_name, author, author_email, github):
        if github:
            command = f"python manage.py create_calcrule_module '{module_name}' '{author}' '{author_email}' --github"
        else:
            command = f"python manage.py create_calcrule_module '{module_name}' '{author}' '{author_email}'"
        result = os.system(command)
        if result != 0:
            raise CommandError(f'Error on adding new calculation module')
        else:
            self.__print_success('Successfully added new calculation module')

    def __print_success(self, msg: str):
        """ Print message to inform about the command progress """
        self.stdout.write(self.style.SUCCESS(msg))

    def __print_info(self, msg: str):
        """ Print message to inform about the command progress = info """
        self.stdout.write(self.style.WARNING(msg))

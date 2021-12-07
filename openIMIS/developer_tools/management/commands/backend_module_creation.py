import os
import json

from ...skeletons import get_skeleton_readme, get_skeleton_urls, get_skeleton_setup
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from git import Repo
from openIMIS.openimisapps import openimis_apps
from pathlib import Path


class Command(BaseCommand):
    help = "This command will generate backend module skeleton in one command"

    def add_arguments(self, parser):
        parser.add_argument('module_name', type=str)
        parser.add_argument('author', type=str)
        parser.add_argument('author_email', type=str)

    def handle(self, *args, **options):
        # get basic data to create new module like module name, current path/directory
        author = options['author']
        author_email = options['author_email']

        module_name = options['module_name']
        repo_name = f"openimis-be-{module_name}_py"
        base_path = Path(settings.BASE_DIR)
        modules_directory = base_path.parent.parent

        new_module_directory = Path(modules_directory).joinpath(repo_name)

        # check if module exists locally
        if Path(new_module_directory).joinpath(module_name).exists():
            raise CommandError("Module already exists in workspace")

        app_directory = self.__create_project_folder(module_name, new_module_directory)

        Repo.init(new_module_directory)

        self.__create_skeleton_module(module_name, app_directory)
        self.__add_setup_file(new_module_directory, module_name, author, author_email)
        self.__add_readme_file(new_module_directory, module_name)
        self.__add_urls_file(app_directory)
        self.__install_module(module_name, new_module_directory)
        self.__add_module_to_openimis_json(base_path, module_name)

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

    def __add_readme_file(self, new_module_directory, module_name):
        self.__add_file(new_module_directory, 'README.md', get_skeleton_readme(module_name))

    def __add_urls_file(self, app_directory):
        self.__add_file(app_directory, 'urls.py', get_skeleton_urls())

    def __add_setup_file(self, new_module_directory, module_name, author, author_email):
        self.__add_file(new_module_directory, 'setup.py', get_skeleton_setup(module_name, author, author_email))

    def __install_module(self, module_name, new_module_directory):
        result = os.system(f'pip install -e {Path(f"{new_module_directory}/")}')
        if result != 0:
            raise CommandError(f'Failed during installation of module {module_name}')
        else:
            self.__print_success(f'Succesfully installed module {module_name}')

    def __add_module_to_openimis_json(self, base_path, module_name):
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

    def __add_file(self, new_module_directory, filename, file_content):
        file = new_module_directory.joinpath(filename)
        with open(file, "w+") as f:
            f.write(file_content)
        self.__print_success(f'Succesfully created {filename} file')

    def __print_success(self, msg: str):
        self.stdout.write(self.style.SUCCESS(msg))

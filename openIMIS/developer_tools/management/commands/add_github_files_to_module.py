import os
import json

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from git import Repo
from pathlib import Path


class Command(BaseCommand):
    help = "This command will add CI to the backend module"

    def add_arguments(self, parser):
        parser.add_argument('module_name', type=str)

    def handle(self, *args, **options):
        module_name = options['module_name']
        repo_name = f"openimis-be-{module_name}_py"
        base_path = Path(settings.BASE_DIR)
        modules_directory = base_path.parent.parent

        module_directory = Path(modules_directory).joinpath(repo_name)

        if not Path(module_directory).joinpath(module_name).exists():
            raise CommandError("Cannot add CI! Module doesn not exist in workspace!")

        github_directory = Path(module_directory).joinpath('.github')
        workflows_directory = Path(github_directory).joinpath('workflows')

        if Path(github_directory).joinpath(workflows_directory).exists():
            raise CommandError("GitHub folder already exists!")

        github_directory.mkdir()
        workflows_directory.mkdir()

        skeletons_folder = Path(base_path).joinpath('developer_tools').joinpath('skeletons')

        self.__add_ci_file(skeletons_folder, workflows_directory)
        self.__add_python_publish_file(skeletons_folder, workflows_directory)
        self.__add_gitignore_file(skeletons_folder, module_directory)

    def __add_ci_file(self, skeletons_folder, workflows_directory):
        file_content = self.__replace_skeleton_values(skeletons_folder, 'openmis-module-test.yml')
        self.__add_file(workflows_directory, 'openmis-module-test.yml', file_content)

    def __add_python_publish_file(self, skeletons_folder, workflows_directory):
        file_content = self.__replace_skeleton_values(skeletons_folder, 'python-publish.yml')
        self.__add_file(workflows_directory, 'python-publish.yml', file_content)

    def __add_gitignore_file(self, skeletons_folder, module_directory):
        file_content = self.__replace_skeleton_values(skeletons_folder, '.gitignore')
        self.__add_file(module_directory, '.gitignore', file_content)

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
        self.__print_info(file)
        with open(file, "w+") as f:
            f.write(file_content)
        self.__print_success(f'Succesfully created {filename} file')

    def __print_success(self, msg: str):
        """ Print message to inform about the command progress  - success"""
        self.stdout.write(self.style.SUCCESS(msg))

    def __print_info(self, msg: str):
        """ Print message to inform about the command progress = info """
        self.stdout.write(self.style.WARNING(msg))

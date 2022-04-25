import git
import json

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from pathlib import Path

from openIMIS.openimisapps import openimis_apps


class Command(BaseCommand):
    help = "This command will extract translations in one command within folder"

    def handle(self, *args, **options):
        self.__print_info(f'starting extracting translations from frontend modules')
        output = self.extract_translations_frontend()
        self.__print_success('finished extracting translations from frontend modules')
        self.__print_info(f'{output}')

    def extract_translations_frontend(self):
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

        extracted_translations = self.__create_translation_folder(modules_directory)

        # take the module names from fe openimis.json
        modules = self.__read_frontend_openimis_file(modules_directory)

        for module in modules:
            try:
                repo_name = f"openimis-{module}_js"
                module_directory = Path(modules_directory).joinpath(repo_name)
                self.__check_module_exist_locally_frontend(module_directory, module)
                translation_file = Path(module_directory).joinpath('src').joinpath('translations').joinpath('en.json')
                if Path(translation_file).exists():
                    with open(translation_file, 'r') as file:
                        translations = json.load(file)
                        with open(extracted_translations.joinpath(f'{module}-en.json'), 'w') as f:
                            json.dump(translations, f, indent=4)
                output_messages.append({
                    'module': module,
                    'message': 'ok'
                })
            except Exception as exc:
                output_messages.append({
                    'module': module,
                    'message': f'Operation failed: {exc}'
                })
        return output_messages

    def __create_translation_folder(self, modules_directory):
        extracted_translations = modules_directory.joinpath('openimis-be_py').joinpath('extracted_translations_fe')
        if not Path(extracted_translations).exists():
            extracted_translations.mkdir()
        return extracted_translations

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

    def __check_module_exist_locally_frontend(self, module_directory, module):
        # check if frontend module exists locally
        if not Path(module_directory).exists():
            git.Repo.clone_from(
                f'https://github.com/openimis/openimis-{module}_js.git',
                module_directory
            )

    def __print_success(self, msg: str):
        """ Print message to inform about the command progress """
        self.stdout.write(self.style.SUCCESS(msg))

    def __print_info(self, msg: str):
        """ Print message to inform about the command progress = info """
        self.stdout.write(self.style.WARNING(msg))

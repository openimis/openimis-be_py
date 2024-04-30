import os
import requests

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from pathlib import Path

from openIMIS.openimisapps import openimis_apps


class Command(BaseCommand):
    help = "This command will upload dashboards config including charts, visualizations, indexes" \
           "if the opensearch is available in package."

    def add_arguments(self, parser):
        parser.add_argument('--host-domain', dest='host_domain', type=str, help='Host domain for opensearch endpoint')
        parser.add_argument('--imis-password', dest='imis_password', type=str, help='Password for IMIS')

    def handle(self, *args, **options):
        host_domain = options.get('host_domain', 'http://localhost:8080')
        imis_password = options.get('imis_password')

        # Check if the 'opensearch_reports' app is in INSTALLED_APPS
        if 'opensearch_reports' in apps.app_configs:
            self.__print_info(f'starting uploading opensearch configurations')
            self.upload_opensearch_configuration(host_domain, imis_password)
            self.__print_success('finished uploading opensearch dashboard configurations')
        else:
            self.__print_info(f'opensearch module not included in package, skipped')

    def upload_opensearch_configuration(self, host_domain, imis_password):
        """
           function to upload dashboards configruration
           through API opensearch endpoint
        """
        base_path = Path(settings.BASE_DIR)
        modules_directory = base_path.parent.parent
        if not Path(modules_directory).joinpath('openimis-fe_js').exists():
            raise Exception("Main assembly frontend module not presented locally")

        opensearch_endpoint = f'{host_domain}/opensearch/api/saved_objects/_import?overwrite=true'
        self.__upload_data(host_domain, opensearch_endpoint, imis_password)

    def __upload_data(self, host_domain, opensearch_endpoint, imis_password):
        base_path = Path(settings.BASE_DIR)
        skeletons_folder = Path(base_path).joinpath('developer_tools').joinpath('opensearch_configuration')
        ndjson_file_path = os.path.join(skeletons_folder, 'opensearch_config.ndjson')

        with open(ndjson_file_path, 'r') as file:
            ndjson_data = file.read()

        username = 'Admin'
        token = self.__get_jwt_token(host_domain, username, imis_password)

        if token:
            headers = {
                'Authorization': f'Bearer {token}',
                'osd-xsrf': 'true'
            }

            files = {
                'file': ('opensearch_config.ndjson', ndjson_data, 'application/octet-stream')
            }
            try:
                response = requests.post(opensearch_endpoint, files=files, headers=headers)
                self.__print_info(response.json())
                if response.status_code == 200:
                    self.__print_info("Data upload successful!")
                else:
                    self.__print_info(f"Failed to upload data. Status code: {response.status_code}")
                    self.__print_info(f"Response: {response.text}")

            except Exception as e:
                self.__print_info(f"An error occurred: {str(e)}")

    def __get_jwt_token(self, host_domain, username, password):
        payload = {
            "username": username,
            "password": password
        }

        headers = {
            'content-type': 'application/json'
        }
        try:
            response = requests.post(f"{host_domain}/api/api_fhir_r4/login/", json=payload,
                                     headers=headers)
            if response.status_code == 200:
                token = response.json().get('token')
                return token
            else:
                self.__print_info(f"Failed to get JWT token. Status code: {response.status_code}")
                self.__print_info(f"Response: {response.text}")
                return None

        except Exception as e:
            self.__print_info(f"An error occurred: {str(e)}")
            return None

    def __print_success(self, msg: str):
        self.stdout.write(self.style.SUCCESS(msg))

    def __print_info(self, msg: str):
        self.stdout.write(self.style.WARNING(msg))

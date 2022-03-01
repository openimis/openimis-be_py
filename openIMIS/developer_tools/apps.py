import logging
from django.apps import AppConfig

logger = logging.getLogger(__name__)


class DeveloperToolsConfig(AppConfig):
    name = 'developer_tools'

    def ready(self):
        pass

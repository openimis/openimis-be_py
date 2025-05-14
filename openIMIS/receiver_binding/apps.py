import logging
from django.apps import AppConfig
from django.conf import settings
import importlib.util

logger = logging.getLogger(__name__)


class ReceiversBindingConfig(AppConfig):
    name = 'receiver_binding'

    def ready(self):
        self.bind_reveivers()

    def bind_reveivers(self):
        for app in settings.OPENIMIS_APPS:
            self._bind_app_reveivers(app)

    def _bind_app_reveivers(self, app_):
        try:
            schema = __import__(f"{app_}.receivers")
        except ModuleNotFoundError as exc:
            # The module doesn't have a schema.py, just skip
            #logger.debug(f"{app} has no reciever module, skipping")
            pass     
        except Exception as exc:
            raise
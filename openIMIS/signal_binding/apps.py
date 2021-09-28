import io
import json
import os

from django.apps import AppConfig
import logging
from django.apps import AppConfig


logger = logging.getLogger(__name__)


class SignalBindingConfig(AppConfig):
    name = 'signal_binding'

    def ready(self):
        self.bind_service_signals()

    def bind_service_signals(self):
        def extract_app(module):
            return "%s" % (module["name"])

        def openimis_apps():
            OPENIMIS_CONF = load_openimis_conf()
            return [*map(extract_app, OPENIMIS_CONF["modules"])]

        def load_openimis_conf(conf_file_param='../openimis.json'):
            conf_json_env = os.environ.get("OPENIMIS_CONF_JSON", "")
            conf_file_path = os.environ.get("OPENIMIS_CONF", conf_file_param)
            if not conf_json_env:
                with open(conf_file_path) as conf_file:
                    return json.load(conf_file)
            else:
                conf_json_env = io.StringIO(conf_json_env)
                return json.load(conf_json_env)

        for app in openimis_apps():
            self._bind_app_signals(app)

    def _bind_app_signals(self, app_):
        try:
            signals_module = __import__(f"{app_}.signals")
            if hasattr(signals_module.signals, "bind_service_signals"):
                signals_module.signals.bind_service_signals()
                logger.debug(f"{app_} service signals connected")
            else:
                logger.debug(f"{app_} has a signals module but no bind_service_signals function")
        except ModuleNotFoundError as exc:
            logger.debug(f"{app_} has no signals module, skipping")
        except Exception as exc:
            logger.debug(f"{app_}: unknown exception occurred during bind_service_signals: {exc}")
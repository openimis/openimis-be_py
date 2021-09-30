import logging
from django.apps import AppConfig
from django.conf import settings

logger = logging.getLogger(__name__)


class SignalBindingConfig(AppConfig):
    name = 'signal_binding'

    def ready(self):
        self.bind_service_signals()

    def bind_service_signals(self):
        for app in settings.OPENIMIS_APPS:
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

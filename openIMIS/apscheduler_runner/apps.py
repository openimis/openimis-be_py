import logging

from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from django.conf import settings
from django.apps import AppConfig
from copy import deepcopy
import importlib.util


logger = logging.getLogger(__name__)


class ApschedulerRunnerConfig(AppConfig):
    name = 'apscheduler_runner'
    scheduler = None

    def ready(self):
        self.setup_module_scheduled_tasks()

    def setup_module_scheduled_tasks(self):
        if settings.SCHEDULER_AUTOSTART:
            self._setup_scheduler_background_task()

    def _setup_scheduler_background_task(self):
        self.scheduler = BackgroundScheduler(deepcopy(settings.SCHEDULER_CONFIG))
        for app in settings.OPENIMIS_APPS:
            self.__add_module_tasks_to_scheduler(app)
        self.scheduler.start()

    def __add_module_tasks_to_scheduler(self, app_):
        spec = importlib.util.find_spec(f"{app_}.scheduled_tasks")
        if spec:
            try:
                app = __import__(f"{app_}.scheduled_tasks")
                app.scheduled_tasks.schedule_tasks(self.scheduler)
                logger.debug(f"{app_} tasks scheduled")
            except Exception as exc:
                logger.debug(f"{app_}: unknown exception occurred during registering scheduled tasks: {exc}")
        else:
            logger.debug(f"{app_} has no scheduled_tasks module, skipping")
        

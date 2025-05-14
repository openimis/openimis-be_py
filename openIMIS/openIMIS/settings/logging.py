import os
from .common import DEBUG

DEFAULT_LOGGING_HANDLER = os.getenv("DJANGO_LOG_HANDLER", "console")
DEFAULT_DB_LOGGING_HANDLER = os.getenv("DJANGO_DB_LOG_HANDLER", "db-queries")
LOGGING_LEVEL = os.getenv("DJANGO_LOG_LEVEL", "DEBUG" if DEBUG else "WARNING")




LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
        "short": {"format": "%(name)s: %(message)s"},
    },
    "handlers": {
        "db-queries": {
            "level": LOGGING_LEVEL,
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.environ.get("DB_QUERIES_LOG_FILE", "db-queries.log"),
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 10,
            "formatter": "standard",
        },
        "debug-log": {
            "level": LOGGING_LEVEL,
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.environ.get("DEBUG_LOG_FILE", "debug.log"),
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 3,
            "formatter": "standard",
        },
        "console": {"class": "logging.StreamHandler", "formatter": "short"},
    },
    "loggers": {
        "": {
            "level": LOGGING_LEVEL,
            "handlers": [DEFAULT_LOGGING_HANDLER],
        },
        "django.db.backends": {
            "level": LOGGING_LEVEL,
            "propagate": False,
            "handlers": [DEFAULT_DB_LOGGING_HANDLER],
        },
        "openIMIS": {
            "level": LOGGING_LEVEL,
            "handlers": [DEFAULT_LOGGING_HANDLER],
        },
    },
}
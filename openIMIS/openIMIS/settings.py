"""
Django settings for openIMIS project.
"""
import json
import logging
import os

from dotenv import load_dotenv
from .openimisapps import openimis_apps, get_locale_folders
from datetime import timedelta

load_dotenv()

# Makes openimis_apps available to other modules
OPENIMIS_APPS = openimis_apps()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOGGING_LEVEL = os.getenv("DJANGO_LOG_LEVEL", "WARNING")
DEFAULT_LOGGING_HANDLER = os.getenv("DJANGO_LOG_HANDLER", "debug-log")

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
            "handlers": ["db-queries"],
        },
        "openIMIS": {
            "level": LOGGING_LEVEL,
            "handlers": [DEFAULT_LOGGING_HANDLER],
        },
    },
}

SENTRY_DSN = os.environ.get("SENTRY_DSN", None)
SENTRY_SAMPLE_RATE = os.environ.get("SENTRY_SAMPLE_RATE", "0.2")
IS_SENTRY_ENABLED = False

if SENTRY_DSN is not None:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration

        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[DjangoIntegration()],
            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            # We recommend adjusting this value in production,
            traces_sample_rate=float(SENTRY_SAMPLE_RATE),
            # If you wish to associate users to errors (assuming you are using
            # django.contrib.auth) you may enable sending PII data.
            send_default_pii=True,
            # By default the SDK will try to use the SENTRY_RELEASE
            # environment variable, or infer a git commit
            # SHA as release, however you may want to set
            # something more human-readable.
            # release="myapp@1.0.0",
        )
        IS_SENTRY_ENABLED = True
    except ModuleNotFoundError:
        logging.error(
            "sentry_sdk has to be installed to use Sentry. Run `pip install --upgrade sentry_sdk` to install it."
        )


def SITE_ROOT():
    root = os.environ.get("SITE_ROOT", "")
    if root == "":
        return root
    elif root.endswith("/"):
        return root
    else:
        return "%s/" % root


def SITE_URL():
    url = os.environ.get("SITE_URL", "")
    if url == "":
        return url
    elif url.endswith("/"):
        return url[:-1]
    else:
        return url


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "SECRET_KEY", "chv^^7i_v3-04!rzu&qe#+h*a=%h(ib#5w9n$!f2q7%2$qp=zz"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
# SECURITY WARNING: don't run without row security in production!
# Row security is dedicated to filter the data result sets according to users' right
# Example: user registered at a Health Facility should only see claims recorded for that Health Facility
ROW_SECURITY = os.environ.get("ROW_SECURITY", "True").lower() == "true"

if "ALLOWED_HOSTS" in os.environ:
    ALLOWED_HOSTS = json.loads(os.environ["ALLOWED_HOSTS"])
else:
    ALLOWED_HOSTS = ["*"]

# TEST_WITHOUT_MIGRATIONS_COMMAND = 'django_nose.management.commands.test.Command'
# TEST_RUNNER = 'core.test_utils.UnManagedModelTestRunner'

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "graphene_django",
    "graphql_jwt.refresh_token.apps.RefreshTokenConfig",
    "test_without_migrations",
    "rest_framework",
    "rules",
    "health_check",  # required
    "health_check.db",  # stock Django health checkers
    "health_check.cache",
    "health_check.storage",
    "django_apscheduler",
    "channels",  # Websocket support
    "developer_tools",
    "drf_spectacular"  # Swagger UI for FHIR API
]
INSTALLED_APPS += OPENIMIS_APPS
INSTALLED_APPS += ["apscheduler_runner", "signal_binding"]  # Signal binding should be last installed module

AUTHENTICATION_BACKENDS = []

if os.environ.get("REMOTE_USER_AUTHENTICATION", "false").lower() == "true":
    AUTHENTICATION_BACKENDS += ["django.contrib.auth.backends.RemoteUserBackend"]

AUTHENTICATION_BACKENDS += [
    "rules.permissions.ObjectPermissionBackend",
    "graphql_jwt.backends.JSONWebTokenBackend",
    "django.contrib.auth.backends.ModelBackend",
]

ANONYMOUS_USER_NAME = None

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "core.jwt_authentication.JWTAuthentication",
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "EXCEPTION_HANDLER": "openIMIS.ExceptionHandlerDispatcher.dispatcher",
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'FHIR R4',
    'DESCRIPTION': 'openIMIS FHIR R4 API',
    'VERSION': '1.0.0',
    'AUTHENTICATION_WHITELIST': [
        'core.jwt_authentication.JWTAuthentication',
        'api_fhir_r4.views.CsrfExemptSessionAuthentication'
    ],
}

if os.environ.get("REMOTE_USER_AUTHENTICATION", "false").lower() == "true":
    REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"].insert(
        0,
        "rest_framework.authentication.RemoteUserAuthentication",
    )

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
]

if DEBUG:
    # Attach profiler middleware
    MIDDLEWARE.append(
        "django_cprofile_middleware.middleware.ProfilerMiddleware"
    )
    DJANGO_CPROFILE_MIDDLEWARE_REQUIRE_STAFF = False

if os.environ.get("REMOTE_USER_AUTHENTICATION", "false").lower() == "true":
    MIDDLEWARE += ["core.security.RemoteUserMiddleware"]
MIDDLEWARE += [
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "openIMIS.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "openIMIS.wsgi.application"

GRAPHENE = {
    "SCHEMA": "openIMIS.schema.schema",
    "RELAY_CONNECTION_MAX_LIMIT": 100,
    "GRAPHIQL_HEADER_EDITOR_ENABLED": True,
    "MIDDLEWARE": [
        "openIMIS.tracer.TracerMiddleware",
        "openIMIS.schema.GQLUserLanguageMiddleware",
        "graphql_jwt.middleware.JSONWebTokenMiddleware",
        "graphene_django.debug.DjangoDebugMiddleware",  # adds a _debug query to graphQL with sql debug info
    ],
}

GRAPHQL_JWT = {
    "JWT_VERIFY_EXPIRATION": True,
    "JWT_LONG_RUNNING_REFRESH_TOKEN": True,
    "JWT_EXPIRATION_DELTA": timedelta(days=1),
    "JWT_REFRESH_EXPIRATION_DELTA": timedelta(days=30),
    "JWT_AUTH_HEADER_PREFIX": "Bearer",
    "JWT_ENCODE_HANDLER": "core.jwt.jwt_encode_user_key",
    "JWT_DECODE_HANDLER": "core.jwt.jwt_decode_user_key",
    # This can be used to expose some resources without authentication
    "JWT_ALLOW_ANY_CLASSES": [
        "graphql_jwt.mutations.ObtainJSONWebToken",
        "graphql_jwt.mutations.Verify",
        "graphql_jwt.mutations.Refresh",
        "graphql_jwt.mutations.Revoke",
        "core.schema.ResetPasswordMutation",
        "core.schema.SetPasswordMutation",
    ],
}

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DB_ENGINE = os.environ.get("DB_ENGINE", "mssql")  # sql_server.pyodbc is deprecated for Django 3.1+

if "sql_server.pyodbc" in DB_ENGINE or "mssql" in DB_ENGINE:
    MSSQL = True
else:
    MSSQL = False

if "DB_OPTIONS" in os.environ:
    DATABASE_OPTIONS = json.loads(os.environ["DB_OPTIONS"])
elif MSSQL:
    if os.name == "nt":
        DATABASE_OPTIONS = {
            "driver": "ODBC Driver 17 for SQL Server",
            "extra_params": "Persist Security Info=False;server=%s"
            % os.environ.get("DB_HOST"),
            "unicode_results": True,
        }
    else:
        DATABASE_OPTIONS = {
            "driver": "ODBC Driver 17 for SQL Server",
            "unicode_results": True,
        }
else:
    DATABASE_OPTIONS = {'options': '-c search_path=django,public'}

if not os.environ.get("NO_DATABASE", "False") == "True":
    DATABASES = {
        "default": {
            "ENGINE": DB_ENGINE,
            "NAME": os.environ.get("DB_NAME"),
            "USER": os.environ.get("DB_USER"),
            "PASSWORD": os.environ.get("DB_PASSWORD"),
            "HOST": os.environ.get("DB_HOST"),
            "PORT": os.environ.get("DB_PORT"),
            "OPTIONS": DATABASE_OPTIONS,
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': ' ../script/sqlite.db',                      # Or path to database file if using sqlite3.
            'USER': '',                      # Not used with sqlite3.
            'PASSWORD': '',                  # Not used with sqlite3.
            'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        }
    }

# Celery message broker configuration for RabbitMQ. One can also use Redis on AWS SQS
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "amqp://127.0.0.1")

# This scheduler config will:
# - Store jobs in the project database
# - Execute jobs in threads inside the application process, for production use, we could use a dedicated process
SCHEDULER_CONFIG = {
    "apscheduler.jobstores.default": {
        "class": "django_apscheduler.jobstores:DjangoJobStore"
    },
    "apscheduler.executors.processpool": {"type": "threadpool"},
}

SCHEDULER_AUTOSTART = os.environ.get("SCHEDULER_AUTOSTART", False)

# Normally, one creates a "scheduler" method that calls the appropriate scheduler.add_job but since we are in a
# modular architecture and calling only once from the core module, this has to be dynamic.
# This list will be called with scheduler.add_job() as specified:
# Note that the document implies that the time is local and follows DST but that seems false and in UTC regardless
SCHEDULER_JOBS = [
    {
        "method": "core.tasks.openimis_test_batch",
        "args": ["cron"],
        "kwargs": {"id": "openimis_test_batch", "minute": 16, "replace_existing": True},
    },
    {
        "method": "policy.tasks.get_policies_for_renewal",
        "args": ["cron"],
        "kwargs": {"id": "openimis_renewal_batch", "hour": 8, "minute": 30, "replace_existing": True},
    },
    # {
    #     "method": "policy_notification.tasks.send_notification_messages",
    #     "args": ["cron"],
    #     "kwargs": {"id": "openimis_notification_batch", 'day_of_week': '*',
    #                "hour": "8,12,16,20", "replace_existing": True},
    # },
    # {
    #     "method": "claim_ai_quality.tasks.claim_ai_processing",
    #     "args": ["cron"],
    #     "kwargs": {"id": "claim_ai_processing",
    #                "hour": 0
    #                "minute", 30
    #                "replace_existing": True},
    # },
]
# This one is called directly with the scheduler object as first parameter. The methods can schedule things on their own
SCHEDULER_CUSTOM = [
    {
        "method": "core.tasks.sample_method",
        "args": ["sample"],
        "kwargs": {"sample_named": "param"},
    },
]


AUTH_USER_MODEL = "core.User"

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = "en-GB"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = False

# List of places to look for translations, this could include an external translation module
LOCALE_PATHS = get_locale_folders() + [
    os.path.join(BASE_DIR, "locale"),
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATIC_URL = "/%sstatic/" % SITE_ROOT()


ASGI_APPLICATION = "openIMIS.asgi.application"

# Django channels require rabbitMQ server, by default it use 127.0.0.1, port 5672
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_rabbitmq.core.RabbitmqChannelLayer",
        "CONFIG": {
            "host": os.environ.get("CHANNELS_HOST", "amqp://guest:guest@127.0.0.1/"),
            # "ssl_context": ... (optional)
        },
    },
}

# Django email settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = os.environ.get("EMAIL_HOST", "localhost")
EMAIL_PORT = os.environ.get("EMAIL_PORT", "1025")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", False)
EMAIL_USE_SSL = os.environ.get("EMAIL_USE_SSL", False)

# By default, the maximum upload size is 2.5Mb, which is a bit short for base64 picture upload
DATA_UPLOAD_MAX_MEMORY_SIZE = int(os.environ.get('DATA_UPLOAD_MAX_MEMORY_SIZE', 10*1024*1024))


# Insuree number validation. One can use the validator function for specific processing or just specify the length
# and modulo for the typical use case. These two can be overridden from the environment but the validator being a
# function, it is not possible.
#
# def insuree_number_validator(x):
#     if str(x)[0] != "x":
#         return ["don't start with x"]
#     else:
#         return []
#
#
# INSUREE_NUMBER_VALIDATOR = insuree_number_validator
INSUREE_NUMBER_LENGTH = os.environ.get("INSUREE_NUMBER_LENGTH", None)
INSUREE_NUMBER_MODULE_ROOT = os.environ.get("INSUREE_NUMBER_MODULE_ROOT", None)


# There used to be a default password for zip files but for security reasons, it was removed. Trying to export
# without a password defined is going to fail
MASTER_DATA_PASSWORD = os.environ.get("MASTER_DATA_PASSWORD", None)

FRONTEND_URL = os.environ.get("FRONTEND_URL", "")

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

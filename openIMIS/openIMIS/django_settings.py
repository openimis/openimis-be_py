"""
Django settings for openIMIS project.
OpenIMIS have custom solution for adding settings.
Instead of declaring them explicitly in settings.py, which is standard
Django approach (see https://docs.djangoproject.com/en/2.1/topics/settings/)
settings are declared as list of SettingsAttribute objects in django_settings.SETTINGS
and imported from modules (in order of modules loading, starting from assembly) to settings.py.
See 'Adding Django Settings' section of openimis_be README for more information.
"""
import json
import logging
import os

from .modulesettingsloader import SettingsAttribute, SettingsAttributeConflictPolicy as setting_type
from .openimisapps import get_locale_folders


def __auth_backends():
    ab = []
    if os.environ.get("REMOTE_USER_AUTHENTICATION", "false").lower() == "true":
        ab += ["django.contrib.auth.backends.RemoteUserBackend"]

    ab += [
        "rules.permissions.ObjectPermissionBackend",
        "graphql_jwt.backends.JSONWebTokenBackend",
        "django.contrib.auth.backends.ModelBackend",
    ]
    return ab


def __rest_setup():
    drf = {
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "core.jwt_authentication.JWTAuthentication",
            "rest_framework.authentication.BasicAuthentication",
            "rest_framework.authentication.SessionAuthentication",
        ],
        "EXCEPTION_HANDLER": "openIMIS.rest_exception_handler.fhir_rest_api_exception_handler",
    }

    if os.environ.get("REMOTE_USER_AUTHENTICATION", "false").lower() == "true":
        drf["DEFAULT_AUTHENTICATION_CLASSES"].insert(
            0,
            "rest_framework.authentication.RemoteUserAuthentication",
        )
    return drf


def _middleware_setup():
    mid = [
        "django.middleware.security.SecurityMiddleware",
        "whitenoise.middleware.WhiteNoiseMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.locale.LocaleMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
    ]

    if os.environ.get("DEBUG", "False").lower() == "true":
        # Attach profiler middleware
        mid.append(
            "django_cprofile_middleware.middleware.ProfilerMiddleware"
        )

    if os.environ.get("REMOTE_USER_AUTHENTICATION", "false").lower() == "true":
        mid += ["core.security.RemoteUserMiddleware"]

    mid += [
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ]
    return mid


def __db_options():
    if "DB_OPTIONS" in os.environ:
        return json.loads(os.environ["DB_OPTIONS"])
    elif os.name == "nt":
        return {
            "driver": "ODBC Driver 17 for SQL Server",
            "extra_params": "Persist Security Info=False;server=%s"
                            % os.environ.get("DB_HOST"),
            "unicode_results": True,
        }
    else:
        return{
            "driver": "ODBC Driver 17 for SQL Server",
            "unicode_results": True,
        }


def __databases():
    if not os.environ.get("NO_DATABASE_ENGINE", "False") == "True":
        return {
            "default": {
                "ENGINE": os.environ.get("DB_ENGINE", "sql_server.pyodbc"),
                "NAME": os.environ.get("DB_NAME"),
                "USER": os.environ.get("DB_USER"),
                "PASSWORD": os.environ.get("DB_PASSWORD"),
                "HOST": os.environ.get("DB_HOST"),
                "PORT": os.environ.get("DB_PORT"),
                "OPTIONS": __db_options(),
            }
        }
    else:
        return {}


def __scheduler_jobs():
    return [
        {
            "method": "core.tasks.openimis_test_batch",
            "args": ["cron"],
            "kwargs": {"id": "openimis_test_batch", "minute": 16, "replace_existing": True},
        },
        # {
        #     "method": "policy.tasks.get_policies_for_renewal",
        #     "args": ["cron"],
        #     "kwargs": {"id": "openimis_renewal_batch", "hour": 8, "minute": 30, "replace_existing": True},
        # },
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


def __password_validators():
    return [
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


def __site_root():
    root = os.environ.get("SITE_ROOT", "")
    if root == "":
        return root
    elif root.endswith("/"):
        return root
    else:
        return "%s/" % root


def __site_url():
    url = os.environ.get("SITE_URL", "")
    if url == "":
        return url
    elif url.endswith("/"):
        return url[:-1]
    else:
        return url


def __base_logging():
    return {
      "version": 1,
      "disable_existing_loggers": False,
      "formatters": {
          "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
          "short": {"format": "%(name)s: %(message)s"},
      },
      "handlers": {
          "db-queries": {
              "level": os.getenv("DJANGO_LOG_LEVEL", "WARNING"),
              "class": "logging.handlers.RotatingFileHandler",
              "filename": os.environ.get("DB_QUERIES_LOG_FILE", "db-queries.log"),
              "maxBytes": 1024 * 1024 * 5,  # 5 MB
              "backupCount": 10,
              "formatter": "standard",
          },
          "debug-log": {
              "level": os.getenv("DJANGO_LOG_LEVEL", "WARNING"),
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
              "level": os.getenv("DJANGO_LOG_LEVEL", "WARNING"),
              "handlers": [os.getenv("DJANGO_LOG_HANDLER", "debug-log")],
          },
          "django.db.backends": {
              "level": os.getenv("DJANGO_LOG_LEVEL", "WARNING"),
              "propagate": False,
              "handlers": ["db-queries"],
          },
          "openIMIS": {
              "level": os.getenv("DJANGO_LOG_LEVEL", "WARNING"),
              "handlers": [os.getenv("DJANGO_LOG_HANDLER", "debug-log")],
          },
      },
    }


def __initialize_sentry():
    IS_SENTRY_ENABLED = False
    SENTRY_DSN = os.environ.get("SENTRY_DSN", None)
    SENTRY_SAMPLE_RATE = os.environ.get("SENTRY_SAMPLE_RATE", "0.2")
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
    return IS_SENTRY_ENABLED


def __base_installed_apps():
    return  [
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
        "rest_framework_rules",
        "health_check",  # required
        "health_check.db",  # stock Django health checkers
        "health_check.cache",
        "health_check.storage",
        "django_apscheduler",
        "channels",  # Websocket support
        "developer_tools"
    ]


def __templates():
    return [
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


def __graphene():
    return {
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


def __graphene_jwt():
    return {
        "JWT_VERIFY_EXPIRATION": True,
        "JWT_LONG_RUNNING_REFRESH_TOKEN": True,
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


def __scheduler_config():
    return {
        "apscheduler.jobstores.default": {
            "class": "django_apscheduler.jobstores:DjangoJobStore"
        },
        "apscheduler.executors.processpool": {"type": "threadpool"},
    }


def __scheduler_custom():
    return [
        {
            "method": "core.tasks.sample_method",
            "args": ["sample"],
            "kwargs": {"sample_named": "param"},
        },
    ]


def __channel_layers():
    return {
        "default": {
            "BACKEND": "channels_rabbitmq.core.RabbitmqChannelLayer",
            "CONFIG": {
                "host": os.environ.get("CHANNELS_HOST", "amqp://guest:guest@127.0.0.1/"),
                # "ssl_context": ... (optional)
            },
        },
    }


def __base_dir():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def __row_security():
    return os.environ.get("ROW_SECURITY", "True").lower() == "true"


def __allowed_hosts():
    return json.loads(os.environ["ALLOWED_HOSTS"]) if "ALLOWED_HOSTS" in os.environ else ["*"]


def __secret_key():
    return os.environ.get("SECRET_KEY", "chv^^7i_v3-04!rzu&qe#+h*a=%h(ib#5w9n$!f2q7%2$qp=zz")


def __insuree_number_validator(x):
    # Insuree number validation. One can use the validator function for specific processing or just specify the length
    # and modulo for the typical use case. These two can be overridden from the environment but the validator being a
    # function, it is not possible.
    if str(x)[0] != "x":
        return ["don't start with x"]
    else:
        return []


SETTINGS = [
    SettingsAttribute('BASE_DIR', __base_dir(), setting_type.FIX),
    SettingsAttribute('LOGGING_LEVEL', os.getenv("DJANGO_LOG_LEVEL", "WARNING"), setting_type.YIELD),
    SettingsAttribute('DEFAULT_LOGGING_HANDLER', os.getenv("DJANGO_LOG_HANDLER", "debug-log"), setting_type.YIELD),
    SettingsAttribute('LOGGING', __base_logging()),
    # Sentry
    SettingsAttribute('SENTRY_DSN', os.environ.get("SENTRY_DSN", None), setting_type.YIELD),
    SettingsAttribute('SENTRY_SAMPLE_RATE', os.environ.get("SENTRY_SAMPLE_RATE", "0.2"), setting_type.YIELD),
    SettingsAttribute('IS_SENTRY_ENABLED', __initialize_sentry(), setting_type.FIX),

    # SECURITY WARNING: keep the secret key used in production secret!
    SettingsAttribute('SECRET_KEY', __secret_key(), setting_type.FIX),

    # SECURITY WARNING: don't run with debug turned on in production!
    SettingsAttribute('DEBUG', os.environ.get("DEBUG", "False").lower() == "true", setting_type.FIX),

    # SECURITY WARNING: don't run without row security in production!
    # Row security is dedicated to filter the data result sets according to users' right
    # Example: user registered at a Health Facility should only see claims recorded for that Health Facility
    SettingsAttribute('ROW_SECURITY', __row_security(), setting_type.FIX),
    SettingsAttribute('ALLOWED_HOSTS', __allowed_hosts(), setting_type.FIX),
    SettingsAttribute('SITE_ROOT', __site_root, setting_type.FIX),

    SettingsAttribute('SITE_URL', __site_url, setting_type.FIX),

    SettingsAttribute('INSTALLED_APPS', __base_installed_apps()),

    SettingsAttribute('AUTHENTICATION_BACKENDS', __auth_backends()),
    SettingsAttribute('ANONYMOUS_USER_NAME', None),

    SettingsAttribute('REST_FRAMEWORK', __rest_setup()),

    SettingsAttribute('MIDDLEWARE', _middleware_setup()),

    SettingsAttribute('DJANGO_CPROFILE_MIDDLEWARE_REQUIRE_STAFF', False),

    SettingsAttribute('ROOT_URLCONF', "openIMIS.urls"),

    SettingsAttribute('TEMPLATES', __templates()),

    SettingsAttribute('WSGI_APPLICATION', "openIMIS.wsgi.application"),

    SettingsAttribute('GRAPHENE', __graphene()),
    SettingsAttribute('GRAPHQL_JWT', __graphene_jwt(), setting_type.FIX),
    # Database
    # https://docs.djangoproject.com/en/2.1/ref/settings/#databases
    SettingsAttribute('DATABASE_OPTIONS', __db_options()),
    SettingsAttribute('DATABASES', __databases()),

    SettingsAttribute('CELERY_BROKER_URL', os.environ.get("CELERY_BROKER_URL", "amqp://127.0.0.1"), setting_type.FIX),
    SettingsAttribute('SCHEDULER_CONFIG', __scheduler_config(), setting_type.FIX),
    SettingsAttribute('SCHEDULER_AUTOSTART', os.environ.get("SCHEDULER_AUTOSTART", False)),
    SettingsAttribute('SCHEDUER_JOBS', __scheduler_jobs()),
    SettingsAttribute('SCHEDULER_CUSTOM', __scheduler_custom()),

    SettingsAttribute('AUTH_USER_MODEL', "core.User"),
    SettingsAttribute('AUTH_PASSWORD_VALIDATORS', __password_validators()),

    # Internationalization
    # https://docs.djangoproject.com/en/2.1/topics/i18n/
    SettingsAttribute('LANGUAGE_CODE', "en-GB"),
    SettingsAttribute('TIME_ZONE', "UTC"),
    SettingsAttribute('USE_I18N', True),
    SettingsAttribute('USE_L10N', True),
    SettingsAttribute('USE_TZ', False),
    SettingsAttribute('LOCALE_PATHS', get_locale_folders() + [
        os.path.join(__base_dir(), "locale"),
    ]),
    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/2.1/howto/static-files/
    SettingsAttribute('STATIC_ROOT', os.path.join(__base_dir(), "staticfiles")),
    SettingsAttribute('STATICFILES_STORAGE', "whitenoise.storage.CompressedManifestStaticFilesStorage"),
    SettingsAttribute('STATIC_URL', "/%sstatic/" % __site_root()),

    # Django channels require rabbitMQ server, by default it use 127.0.0.1, port 5672
    SettingsAttribute('ASGI_APPLICATION', "openIMIS.asgi.application"),
    SettingsAttribute('CHANNEL_LAYERS', __channel_layers()),

    # Django email settings
    SettingsAttribute('EMAIL_BACKEND', "django.core.mail.backends.smtp.EmailBackend"),
    SettingsAttribute('EMAIL_HOST', os.environ.get("EMAIL_HOST", "localhost")),
    SettingsAttribute('EMAIL_PORT', os.environ.get("EMAIL_PORT", "1025")),
    SettingsAttribute('EMAIL_HOST_USER', os.environ.get("EMAIL_HOST_USER", "")),
    SettingsAttribute('EMAIL_HOST_PASSWORD', os.environ.get("EMAIL_HOST_PASSWORD", "")),
    SettingsAttribute('EMAIL_USE_TLS', os.environ.get("EMAIL_USE_TLS", False)),
    SettingsAttribute('EMAIL_USE_SSL', os.environ.get("EMAIL_USE_SSL", False)),

    # By default, the maximum upload size is 2.5Mb, which is a bit short
    # for base64 picture upload
    SettingsAttribute('DATA_UPLOAD_MAX_MEMORY_SIZE',
                      int(os.environ.get('DATA_UPLOAD_MAX_MEMORY_SIZE', 10*1024*1024))),
    SettingsAttribute('INSUREE_NUMBER_LENGTH', os.environ.get("INSUREE_NUMBER_LENGTH", None)),
    SettingsAttribute('INSUREE_NUMBER_MODULE_ROOT', os.environ.get("INSUREE_NUMBER_MODULE_ROOT", None)),

    # SettingsAttribute('TEST_WITHOUT_MIGRATIONS_COMMAND', 'django_nose.management.commands.test.Command'),
    # SettingsAttribute('TEST_RUNNER', 'core.test_utils.UnManagedModelTestRunner'),
    # SettingsAttribute('INSUREE_NUMBER_VALIDATOR', __insuree_number_validator),

    SettingsAttribute('FRONTEND_URL', os.environ.get("FRONTENT_URL", "")),
]


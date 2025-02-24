"""
Django settings for openIMIS project.
"""
import json
import logging
import os

from ..openimisapps import openimis_apps, get_locale_folders
from datetime import timedelta
from .common import DEBUG, BASE_DIR, MODE
from .security import REMOTE_USER_AUTHENTICATION

# Makes openimis_apps available to other modules
OPENIMIS_APPS = openimis_apps()


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


SITE_FRONT = os.environ.get("SITE_FRONT", "front")
FRONTEND_URL = SITE_ROOT() + SITE_FRONT

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
    "drf_spectacular",  # Swagger UI for FHIR API
    "axes",
    "django_opensearch_dsl",
]
INSTALLED_APPS += OPENIMIS_APPS
INSTALLED_APPS += ["apscheduler_runner", "signal_binding", "receiver_binding"]  # Signal binding should be last installed module

AUTHENTICATION_BACKENDS = []

if os.environ.get("REMOTE_USER_AUTHENTICATION", "false").lower() == "true":
    AUTHENTICATION_BACKENDS += ["django.contrib.auth.backends.RemoteUserBackend"]

AUTHENTICATION_BACKENDS += [
    "axes.backends.AxesStandaloneBackend",
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
if REMOTE_USER_AUTHENTICATION: 
    REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"].insert(
        0,
        "rest_framework.authentication.RemoteUserAuthentication",
    )

SPECTACULAR_SETTINGS = {
    'TITLE': 'FHIR R4',
    'DESCRIPTION': 'openIMIS FHIR R4 API',
    'VERSION': '1.0.0',
    'AUTHENTICATION_WHITELIST': [
        'core.jwt_authentication.JWTAuthentication',
        'api_fhir_r4.views.CsrfExemptSessionAuthentication'
    ],
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'core.middleware.GraphQLRateLimitMiddleware',
    "axes.middleware.AxesMiddleware",
    "core.middleware.DefaultAxesAttributesMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "core.middleware.SecurityHeadersMiddleware",
]

if DEBUG:
    # Attach profiler middleware
    MIDDLEWARE.append(
        "django_cprofile_middleware.middleware.ProfilerMiddleware"
    )
    DJANGO_CPROFILE_MIDDLEWARE_REQUIRE_STAFF = False

if REMOTE_USER_AUTHENTICATION:
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
        "graphql_jwt.middleware.JSONWebTokenMiddleware"
    ],
}

if DEBUG:
    GRAPHENE['MIDDLEWARE'] += [
        "graphene_django.debug.DjangoDebugMiddleware"  # adds a _debug query to graphQL with sql debug info
    ]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATIC_URL = "/%sstatic/" % SITE_ROOT()


ASGI_APPLICATION = "openIMIS.asgi.application"


# Django email settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "localhost")
EMAIL_PORT = os.environ.get("EMAIL_PORT", "1025")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", False)
EMAIL_USE_SSL = os.environ.get("EMAIL_USE_SSL", False)

# By default, the maximum upload size is 2.5Mb, which is a bit short for base64 picture upload
DATA_UPLOAD_MAX_MEMORY_SIZE = int(os.environ.get('DATA_UPLOAD_MAX_MEMORY_SIZE', 10 * 1024 * 1024))


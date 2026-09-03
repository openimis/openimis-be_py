"""
Django settings for openIMIS project.
"""
import ast
import json
import logging
import os
import sys
from pathlib import Path

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
FRONTEND_URL = (
    'https://' if 'https' in os.environ.get("PROTOS", '') else 'http://'
    ) + SITE_URL() + '/' + SITE_FRONT

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
IS_TESTING =  'test' in sys.argv


def _locate_module_file(module_dotted_path):
    """Find a module file on sys.path without importing it."""
    relative = Path(*module_dotted_path.split("."))
    for entry in sys.path:
        base = Path(entry)
        for candidate in (
            base / relative.with_suffix(".py"),
            base / relative / "__init__.py",
        ):
            if candidate.is_file():
                return candidate
    return None


_CORE_EXTENSIONS = {
    "graphql_jwt_backend": (
        "core.jwt_authentication.JSONWebTokenBackend",
        "graphql_jwt.backends.JSONWebTokenBackend",
    ),
    "graphql_jwt_middleware": (
        "core.middleware.CustomJSONWebTokenMiddleware",
        "graphql_jwt.middleware.JSONWebTokenMiddleware",
    ),
    "graphql_rate_limit": (
        "core.middleware.GraphQLRateLimitMiddleware",
        None,
    ),
    "default_axes_attributes": (
        "core.middleware.DefaultAxesAttributesMiddleware",
        None,
    ),
    "admin_logout": (
        "core.middleware.AdminLogoutMiddleware",
        None,
    ),
    "clear_user_context": (
        "core.middleware.ClearUserContextMiddleware",
        None,
    ),
    "security_headers": (
        "core.middleware.SecurityHeadersMiddleware",
        None,
    ),
    "remote_user": (
        "core.security.RemoteUserMiddleware",
        None,
    ),
}


def _core_module_classes(extensions):
    """Parse each core module source once; return {module_path: set(class_names)}."""
    module_paths = {
        core_path.rpartition(".")[0]
        for core_path, _ in extensions.values()
    }
    classes_by_module = {}
    for module_path in module_paths:
        module_file = _locate_module_file(module_path)
        if module_file is None:
            classes_by_module[module_path] = set()
            continue
        try:
            source = module_file.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (OSError, UnicodeDecodeError, SyntaxError):
            classes_by_module[module_path] = set()
            continue
        classes_by_module[module_path] = {
            node.name
            for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef)
        }
    return classes_by_module


def _resolve_core_extensions(extensions):
    """
    Resolve {name: (core_path, fallback)} to {name: resolved_path}.

    Uses AST inspection instead of import: base.py loads before CACHES and
    importing core at this stage would fail. Each core module source is parsed
    once and reused for every class lookup.
    """
    logger = logging.getLogger(__name__)
    classes_by_module = _core_module_classes(extensions)
    resolved = {}
    for name, (core_path, fallback) in extensions.items():
        module_path, _, class_name = core_path.rpartition(".")
        if class_name in classes_by_module.get(module_path, set()):
            resolved[name] = core_path
        elif fallback:
            logger.warning(
                "core is missing %s (%s); using fallback %s.",
                name,
                core_path,
                fallback,
            )
            resolved[name] = fallback
        else:
            logger.warning(
                "core is missing %s (%s); skipping.",
                name,
                core_path,
            )
            resolved[name] = None
    return resolved


_RESOLVED_CORE = _resolve_core_extensions(_CORE_EXTENSIONS)


def _middleware_stack(*entries):
    return [entry for entry in entries if entry]

AUTHENTICATION_BACKENDS = []

if os.environ.get("REMOTE_USER_AUTHENTICATION", "false").lower() == "true":
    AUTHENTICATION_BACKENDS += ["django.contrib.auth.backends.RemoteUserBackend"]

AUTHENTICATION_BACKENDS += [
    "axes.backends.AxesStandaloneBackend",
    "rules.permissions.ObjectPermissionBackend",
    _RESOLVED_CORE["graphql_jwt_backend"],
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

MIDDLEWARE = _middleware_stack(
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    _RESOLVED_CORE["graphql_rate_limit"],
    "axes.middleware.AxesMiddleware",
    _RESOLVED_CORE["default_axes_attributes"],
    _RESOLVED_CORE["admin_logout"],
    "django.contrib.sessions.middleware.SessionMiddleware",
    _RESOLVED_CORE["clear_user_context"],
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
    _RESOLVED_CORE["security_headers"],
    "csp.middleware.CSPMiddleware",
)

if DEBUG:
    # Attach profiler middleware
    MIDDLEWARE.append(
        "django_cprofile_middleware.middleware.ProfilerMiddleware"
    )
    DJANGO_CPROFILE_MIDDLEWARE_REQUIRE_STAFF = False

if REMOTE_USER_AUTHENTICATION:
    MIDDLEWARE += _middleware_stack(_RESOLVED_CORE["remote_user"])
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
        _RESOLVED_CORE["graphql_jwt_middleware"],
    ],
}

if DEBUG:
    GRAPHENE['MIDDLEWARE'] += [
        "graphene_django.debug.DjangoDebugMiddleware"  # adds a _debug query to graphQL with sql debug info
    ]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = "/%sstatic/" % SITE_ROOT()

MEDIA_URL = "/file_storage/"
MEDIA_ROOT = os.path.join(BASE_DIR, "file_storage/")

if not os.path.exists(MEDIA_ROOT):
    os.makedirs(MEDIA_ROOT)

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    'staticfiles': {
        'BACKEND': "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


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

import os
import json

# Celery message broker configuration for RabbitMQ. One can also use Redis on AWS SQS
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "amqp://rabitmq")
if 'CELERY_RESULT_BACKEND' in os.environ:
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND")

if 'CACHE_BACKEND' in os.environ and 'CACHE_URL' in os.environ:
    CACHE_BACKEND = os.environ.get('CACHE_BACKEND')
    CACHE_URL = os.environ.get("CACHE_URL")
    CACHE_OPTIONS = os.environ.get("CACHE_OPTIONS", None)
    if CACHE_OPTIONS:
        CACHE_OPTIONS = json.loads(CACHE_OPTIONS)
else:
    CACHE_BACKEND = 'django.core.cache.backends.locmem.LocMemCache'
    CACHE_URL = None
    CACHE_OPTIONS = None

CACHE_PARAM = {}
CACHE_PARAM['BACKEND'] = CACHE_BACKEND
if CACHE_URL:
    CACHE_PARAM['LOCATION'] = CACHE_URL

if CACHE_OPTIONS:
    CACHE_PARAM['OPTIONS'] = CACHE_OPTIONS

CACHES = {
    'default': {
        **CACHE_PARAM,
        'KEY_PREFIX': "oi"
    },
    'location': {
        **CACHE_PARAM,
        'KEY_PREFIX': "loc"
    },
    'coverage': {
        **CACHE_PARAM,
        'KEY_PREFIX': "cov"

    }
}

# Django channels require rabbitMQ server, by default it use 127.0.0.1, port 5672
if "CHANNELS_BACKEND" in os.environ and "CHANNELS_HOST" in os.environ:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": os.environ.get("CHANNELS_BACKEND"),
            "CONFIG": {
                "hosts": [os.environ.get("CHANNELS_HOST")],
                # "ssl_context": ... (optional)
            },
        },
    }

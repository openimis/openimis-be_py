"""
Django settings for openIMIS project.
"""
import json
import logging
import os

from ..openimisapps import openimis_apps, get_locale_folders
from datetime import timedelta
from cryptography.hazmat.primitives import serialization
from .common import MODE

from split_settings.tools import optional, include

LOAD_ENV = os.environ.get("LOAD_ENV", '.env')
if LOAD_ENV != '':
    from dotenv import load_dotenv, find_dotenv
    ENV_PATH = find_dotenv(filename=LOAD_ENV)
    load_dotenv(dotenv_path=ENV_PATH)

base_settings = [
    'security.py',
    'base.py',
    'database.py',
    'logging.py',
    'sentry.py',
    'scheduler.py',
    'queue_cache.py',
    'opensearch.py',
    'trad.py',
    f'{MODE}.py'
    # Optional local settings
    #optional('local_settings.py'),
]

# Include the components
include(*base_settings)


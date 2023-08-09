"""
Django settings for openIMIS project.

Settings and values are added to settings.py
through load_settings_from_modules()
"""
from dotenv import load_dotenv

from .openimisapps import openimis_apps
from .modulesettingsloader import load_settings_from_modules


load_dotenv()

# Loads django settings from assembly and modules
load_settings_from_modules()

# Makes openimis_apps available to other modules
OPENIMIS_APPS = openimis_apps()

# Base INSTALLED_APPS are taken from openIMIS.django_settings,
# imis apps and signals are added directly in settings as they should be installed at the end.
INSTALLED_APPS += OPENIMIS_APPS
INSTALLED_APPS += ["signal_binding"]  # Signal binding should be last installed module


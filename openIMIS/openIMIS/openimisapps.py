import os
from importlib import resources

from django.core.management.utils import is_ignored_path

from .openimisconf import load_openimis_conf


def extract_app(module):
    return "%s" % (module["name"])


def openimis_apps():
    OPENIMIS_CONF = load_openimis_conf()
    return [*map(extract_app, OPENIMIS_CONF["modules"])]


def get_locale_folders():
    apps = []
    basedirs = []
    for mod in load_openimis_conf()["modules"]:
        mod_name = mod["name"]
        with resources.path(mod_name, "__init__.py") as path:
            apps.append(path.parent.parent)  # This might need to be more restrictive

    for topdir in ["."] + apps:
        for dirpath, dirnames, filenames in os.walk(topdir, topdown=True):
            for dirname in dirnames:
                if dirname == 'locale':
                    basedirs.append(os.path.join(dirpath, dirname))
    return basedirs

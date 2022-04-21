import os
from importlib import resources

from .openimisconf import load_openimis_conf


def extract_app(module):
    return "%s" % (module["name"])


def openimis_apps():
    OPENIMIS_CONF = load_openimis_conf()
    return [*map(extract_app, OPENIMIS_CONF["modules"])]


def get_locale_folders():
    """
    Get locale folders for the modules in a reverse order to make it easy to override the translations
    """
    apps = []
    basedirs = []
    for mod in load_openimis_conf()["modules"]:
        mod_name = mod["name"]
        with resources.path(mod_name, "__init__.py") as path:
            apps.append(path.parent.parent)  # This might need to be more restrictive

    for topdir in ["."] + apps:
        for dirpath, dirnames, filenames in os.walk(topdir, topdown=True):
            for dirname in dirnames:
                if dirname == "locale":
                    basedirs.insert(0, os.path.join(dirpath, dirname))
    return basedirs

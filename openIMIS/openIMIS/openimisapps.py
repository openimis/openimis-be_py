from .openimisconf import load_openimis_conf


def extract_app(module):
    return "%s" % (module["name"])


def openimis_apps():
    OPENIMIS_CONF = load_openimis_conf()
    return [*map(extract_app, OPENIMIS_CONF["modules"])]

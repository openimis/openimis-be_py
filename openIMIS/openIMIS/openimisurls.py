from django.urls import include, path
from .openimisconf import load_openimis_conf

def extract_url(module):  
    return path('%s/' % module["name"], include('%s.urls' % module["name"]))

def openimis_urls() :
    OPENIMIS_CONF = load_openimis_conf()
    return [*map(extract_url, OPENIMIS_CONF["modules"])]
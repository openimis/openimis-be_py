from django.urls import include, path
from .openimisconf import load_openimis_conf
import os

def extract_url(module):  
    return path('%s%s/' % (os.environ.get("SITE_ROOT", ''), module["name"]), include('%s.urls' % module["name"]))

def openimis_urls() :
    OPENIMIS_CONF = load_openimis_conf()
    return [*map(extract_url, OPENIMIS_CONF["modules"])]
from django.urls import include, path
from .openimisconf import load_openimis_conf
import os
from .settings import SITE_ROOT

def extract_url(module):  
    return path('%s%s/' % (SITE_ROOT(), module["name"]), include('%s.urls' % module["name"]))

def openimis_urls() :
    OPENIMIS_CONF = load_openimis_conf()
    return [*map(extract_url, OPENIMIS_CONF["modules"])]
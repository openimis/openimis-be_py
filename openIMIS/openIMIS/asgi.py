from channels.auth import AuthMiddlewareStack
import json
import os
import logging
import django

from channels.routing import ProtocolTypeRouter, URLRouter
from importlib import import_module

from django.core.asgi import get_asgi_application
from django.urls import path
from .openimisconf import load_openimis_conf
logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'openIMIS.settings')
django.setup()


def SITE_ROOT():
    root = os.environ.get("SITE_ROOT", '')
    if (root == ''):
        return root
    elif (root.endswith('/')):
        return root
    else:
        return "%s/" % root


def extract_websocket_urls(module):
    try:
        module_import = import_module(F"{module['name']}.routing")
        module_routing = module_import.websocket_urlpatterns

        if module_routing is None:
            return []
        return module_routing

    except ModuleNotFoundError as e:
        logger.log(level=logging.INFO,
                   msg=F"Websocket routing for module {module['name']} not found, "
                       F"if you want to attach websocket endpoint add routing.py with websocket_urlpatterns "
                       F"to your module")
        return []
    except Exception as e:
        logger.log(level=logging.ERROR,
                   msg=F"Failed to load websocket routing for module {module['name']}, reason:\n"
                       F"{str(e)}")
        return []


def openimis_websocket_endpoints():
    module_routings_paths = map(extract_websocket_urls, load_openimis_conf()['modules'])
    return [route for module_routings in module_routings_paths for route in module_routings if route]



routings = openimis_websocket_endpoints()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(routings)
})

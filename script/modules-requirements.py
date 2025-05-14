import os
import json
import sys


app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', "openIMIS", "openIMIS")
sys.path.insert(0, app_path)
from openimisconf import load_openimis_conf

conf_file_path = 'openimis.json'

if len(sys.argv) > 1:
    conf_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), sys.argv[1])

if not conf_file_path:
    sys.exit("Missing config file path argument")
if not os.path.isfile(conf_file_path):
    sys.exit("Config file parameter refers to missing file %s" % conf_file_path)


def extract_requirement(module):
    return "%s" % module["pip"]

OPENIMIS_CONF = load_openimis_conf(conf_file_path)
MODULES = list(map(extract_requirement, OPENIMIS_CONF["modules"]))
print("\n".join(MODULES))

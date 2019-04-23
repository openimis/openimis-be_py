import os
import json
import sys
import re

def load_openimis_conf():
    conf_file_path = sys.argv[1]
    if not conf_file_path:
        sys.exit("Missing config file path argument")
    if not os.path.isfile(conf_file_path):
        sys.exit("Config file parameter refers to missing file %s" % conf_file_path)

    with open(conf_file_path) as conf_file:
        return json.load(conf_file)

def extract_test(module):
    return "coverage run --source='.' manage.py test %s -n" % re.split('[^a-zA-Z0-9\-_]',module["pip"])[0]

OPENIMIS_CONF = load_openimis_conf()
MODULES = list(map(extract_test, OPENIMIS_CONF["modules"]))
print("\n".join(MODULES))
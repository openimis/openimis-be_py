import os
import json
import sys

def load_openimis_conf():
    conf_file_path = sys.argv[1]
    if not conf_file_path:
        sys.exit("Missing config file path argument")
    if not os.path.isfile(conf_file_path):
        sys.exit("Config file parameter refers to missing file %s" % conf_file_path)

    with open(conf_file_path) as conf_file:
        return json.load(conf_file)

def extract_requirement(module):
    return "ln -s ../../openimis-be-%s_py %s" % (module["name"], module["name"])

OPENIMIS_CONF = load_openimis_conf()
MODULES = list(map(extract_requirement, OPENIMIS_CONF["modules"]))
print("\n".join(MODULES))
import json
import os


def load_openimis_conf():
    conf_json_env = os.environ.get("OPENIMIS_CONF_JSON", "")
    print(conf_json_env)
    conf_file_path = os.environ.get("OPENIMIS_CONF", "../openimis.json")
    if conf_json_env:
        with open(conf_file_path) as conf_file:
            return json.load(conf_file)
    else:
        with open(conf_file_path) as conf_file:
            return json.load(conf_file)

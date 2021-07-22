import json
import os


def load_openimis_conf():
    conf_file_path = os.environ.get("OPENIMIS_CONF", "../openimis.json")
    with open(conf_file_path) as conf_file:
        return json.load(conf_file)

import json
import os
import io

def load_openimis_conf():
    conf_json_env = os.environ.get("OPENIMIS_CONF_JSON", "")
    conf_file_path = os.environ.get("OPENIMIS_CONF", "../openimis.json")
    if not conf_json_env:
        with open(conf_file_path) as conf_file:
            return json.load(conf_file)
    else:
        conf_json_env = io.StringIO(conf_json_env)
        return json.load(conf_json_env)

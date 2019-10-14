import os
import json
import sys


def load_openimis_conf():
    conf_file_path = "../openimis.json"
    with open(conf_file_path) as conf_file:
        return json.load(conf_file)

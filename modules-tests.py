import os
import json
import sys
import itertools

def load_openimis_conf():
    conf_file_path = sys.argv[1]
    if not conf_file_path:
        sys.exit("Missing config file path argument")
    if not os.path.isfile(conf_file_path):
        sys.exit("Config file parameter refers to missing file %s" % conf_file_path)

    with open(conf_file_path) as conf_file:
        return json.load(conf_file)

def extract_test(module):
    cmds = [
        "echo '-- TESTING %(module)s ---'" % {'module': module["name"]},
        "coverage run --source='%(module)s' manage.py test %(module)s -n" % {'module': module["name"]},
        "coverage report"
    ]
    if "codeclimat" in module:
        cmds += [
            "coverage xml",
            "export CC_TEST_REPORTER_ID=%s" % module["codeclimat"],
            "cc-test-reporter format-coverage -t coverage.py -p ../../openimis-be-%s_py/" % module["name"],
            "cc-test-reporter after-build -p ../../openimis-be-%s_py/" % module["name"]
        ]
    return cmds
OPENIMIS_CONF = load_openimis_conf()
CMDS = list(itertools.chain(*map(extract_test, OPENIMIS_CONF["modules"])))
print("\n".join(CMDS))
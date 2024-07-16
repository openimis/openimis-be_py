import os
import json
import sys
import itertools
from distutils.sysconfig import get_python_lib
app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', "openIMIS", "openIMIS")
sys.path.insert(0, app_path)
from openimisconf import load_openimis_conf

def extract_test(module):
    cmds = [
        "echo '--- TESTING %(module)s ---'" % {'module': module["name"]},
        "coverage run --source='%(module)s' --omit='*/test_*.py' manage.py test %(module)s --keepdb" % {'module': module["name"]},
        "coverage report"
    ]
    codeclimat_key = os.environ.get("CC_TEST_REPORTER_ID_%s" % module["name"])
    escaped_python_lib_path = get_python_lib().replace("/", "\\/")
    if codeclimat_key:
        cmds += [
            "coverage xml",
            "export CC_TEST_REPORTER_ID=%s" % codeclimat_key,
            # "cc-test-reporter format-coverage -t coverage.py -p %s --add-prefix ./" % get_python_lib(), -p flag don't do the job (?!?)
            "cc-test-reporter format-coverage -t coverage.py",
            "sed -i 's/%s\///g' coverage/codeclimate.json" % escaped_python_lib_path,
            "cc-test-reporter upload-coverage"
        ]
    return cmds
OPENIMIS_CONF = load_openimis_conf()
CMDS = [
]
CMDS += list(itertools.chain(*map(extract_test, OPENIMIS_CONF["modules"])))
print("\n".join(CMDS))

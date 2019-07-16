#!/usr/bin/env python
import os
from django.conf import settings
from django.db import connections, connection
from django.test.utils import get_unique_databases_and_mirrors


init_test_db_file = os.path.join(os.path.dirname(__file__), 'init_test_db.sql')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'openIMIS.settings')
import openIMIS.settings
test_databases, mirrored_aliases = get_unique_databases_and_mirrors()
for db_host, db_port, db_engine, db_name in test_databases.keys():
    name, cfgs = test_databases[(db_host, db_port, db_engine, db_name)]
    for cfg in cfgs:
        with connections[cfg]._nodb_connection.cursor() as c:
            c.execute("DROP DATABASE IF EXISTS %s" % db_name)
            c.execute("CREATE DATABASE %s" % db_name)
        os.system("sqlcmd -S %s,%s -U %s -P %s -d %s -i init_test_db.sql" % (db_host, db_port, settings.DATABASES[cfg]['USER'], settings.DATABASES[cfg]['PASSWORD'], db_name))

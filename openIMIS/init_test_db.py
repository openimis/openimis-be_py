#!/usr/bin/env python
import os
from django.conf import settings
from django.db import connections
from django.test.utils import get_unique_databases_and_mirrors


init_test_db_file = os.path.join(os.path.dirname(__file__), 'init_test_db.sql')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'openIMIS.settings')

test_databases, mirrored_aliases = get_unique_databases_and_mirrors()
for db_host, db_port, db_engine, db_name in test_databases.keys():
    name, cfgs = test_databases[(db_host, db_port, db_engine, db_name)]
    for cfg in cfgs:
        if "postgres" in db_engine:
            with connections[cfg].cursor() as c:
                c.execute(f"DROP DATABASE IF EXISTS \"{db_name}\"")
                c.execute(f"CREATE DATABASE \"{db_name}\"")
            os.system("PGPASSWORD='%s' psql -h %s -p %s -U %s %s -f init_test_db_pg.sql" %
                      (settings.DATABASES[cfg]['PASSWORD'], db_host, db_port, settings.DATABASES[cfg]['USER'], db_name))
        else:
            with connections[cfg].cursor() as c:
                c.execute("DROP DATABASE IF EXISTS %s" % db_name)
                c.execute("CREATE DATABASE %s" % db_name)
            os.system("sqlcmd -S %s,%s -U %s -P '%s' -d %s -i init_test_db.sql" %
                      (db_host, db_port, settings.DATABASES[cfg]['USER'], settings.DATABASES[cfg]['PASSWORD'], db_name))

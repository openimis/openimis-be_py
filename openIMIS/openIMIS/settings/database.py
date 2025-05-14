import os
import json
# no db
DATABASES = {}
DB_DEFAULT = os.environ.get("DB_DEFAULT", 'postgresql')

if os.environ.get("NO_DATABASE", "False") == "True":

    DATABASES['default'] = {
        # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ' ../script/sqlite.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
if "DB_OPTIONS" in os.environ:
    DATABASE_OPTIONS = json.loads(os.environ["DB_OPTIONS"])
    MSSQL_DATABASE_OPTIONS = DATABASE_OPTIONS
    PSQL_DATABASE_OPTIONS = DATABASE_OPTIONS
else:
    if os.name == "nt":
        MSSQL_DATABASE_OPTIONS = {
            "driver": "ODBC Driver 17 for SQL Server",
            "extra_params": "Persist Security Info=False;server=%s"
            % os.environ.get("DB_HOST"),
            "unicode_results": True,
        }
    else:
        MSSQL_DATABASE_OPTIONS = {
            "driver": "ODBC Driver 17 for SQL Server",
            "unicode_results": True,
        }
    PSQL_DATABASE_OPTIONS = {'options': '-c search_path=django,public'}

DEFAULT_ENGINE = os.environ.get("DB_ENGINE", "mssql" if DB_DEFAULT == 'mssql' else "django.db.backends.postgresql")
DEFAULT_NAME = os.environ.get("DB_NAME", "imis")
DEFAULT_USER = os.environ.get("DB_USER", "IMISuser")
DEFAULT_PASSWORD = os.environ.get("DB_PASSWORD")
DEFAULT_HOST = os.environ.get("DB_HOST", 'db')
DEFAULT_PORT = os.environ.get("DB_PORT", "1433" if DB_DEFAULT == 'mssql' else "5432")



if DB_DEFAULT == 'mssql':
    DATABASES["default"] = {
        "ENGINE": os.environ.get("MSSQL_DB_ENGINE", DEFAULT_ENGINE),
        "NAME": os.environ.get("MSSQL_DB_NAME", DEFAULT_NAME),
        "USER": os.environ.get("MSSQL_DB_USER", DEFAULT_USER),
        "PASSWORD": os.environ.get("MSSQL_DB_PASSWORD", DEFAULT_PASSWORD),
        "HOST": os.environ.get("MSSQL_DB_HOST", DEFAULT_HOST),
        "PORT": os.environ.get("MSSQL_DB_PORT", DEFAULT_PORT),
        "OPTIONS": MSSQL_DATABASE_OPTIONS,
        'TEST': {
            'NAME': os.environ.get("DB_TEST_NAME", "test_" + os.environ.get("MSSQL_DB_NAME", "imis")),
        }
    }
else:
    DATABASES["default"] = {
        "ENGINE": os.environ.get("PSQL_DB_ENGINE", DEFAULT_ENGINE),
        "NAME": os.environ.get("PSQL_DB_NAME", DEFAULT_NAME),
        "USER": os.environ.get("PSQL_DB_USER", DEFAULT_USER),
        "PASSWORD": os.environ.get("PSQL_DB_PASSWORD", DEFAULT_PASSWORD),
        "HOST": os.environ.get("PSQL_DB_HOST", DEFAULT_HOST),
        "PORT": os.environ.get("PSQL_DB_PORT", DEFAULT_PORT),
        "OPTIONS": PSQL_DATABASE_OPTIONS,
        'TEST': {
            'NAME': os.environ.get("DB_TEST_NAME", "test_" + os.environ.get("MSSQL_DB_NAME", "imis")),
        }
    }

# should not add that config unless used
if "DASHBOARD_DB_ENGINE" in os.environ:
    DATABASES['dashboard_db'] = {
        "ENGINE": os.environ.get("DASHBOARD_DB_ENGINE", DEFAULT_ENGINE),
        "NAME": os.environ.get("DASHBOARD_DB_NAME"),
        "USER": os.environ.get("DASHBOARD_DB_USER"),
        "PASSWORD": os.environ.get("DASHBOARD_DB_PASSWORD"),
        "HOST": os.environ.get("DASHBOARD_DB_HOST", DEFAULT_HOST),
        "PORT": os.environ.get("DASHBOARD_DB_PORT", DEFAULT_PORT)
    }

if "sql_server.pyodbc" in DATABASES["default"]['ENGINE'] or "mssql" in DATABASES["default"]['ENGINE']:
    MSSQL = True

else:
    MSSQL = False

    # Database
    # https://docs.djangoproject.com/en/2.1/ref/settings/#databases


DATABASE_ROUTERS = ["openIMIS.routers.DashboardDatabaseRouter"]


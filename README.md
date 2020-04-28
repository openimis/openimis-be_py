# openIMIS Backend Reference Implementation : Windows Docker
This repository holds the configuration files for the openIMIS Frontend Reference Implementation:

Please look for the direction on the openIMIS Wiki: https://openimis.atlassian.net/wiki/spaces/OP/pages/963182705/MO1.1+Install+the+modular+openIMIS+using+Docker

This repo branches, tags,... are maintained by openIMIS official delivery team who use it to build the official openIMIS Docker images containing the official modules (versions) list.

In case of troubles, please consult/contact our service desk via our [ticketing site](https://openimis.atlassian.net/servicedesk/customer).

# openIMIS Backend Reference Implementation
This repository holds the configuration files for the openIMIS Backend Reference Implementation.
It serves 2 distinct use cases:
- developers who want to implement new modules or modify existing Backend modules of openIMIS
- distributors who want to assemble modules into a Docker image for delivery

This repo branches, tags,... are maintained by openIMIS official delivery team who use it to build the official openIMIS Docker images containing the official modules (versions) list.

In case of troubles, please consult/contact our service desk via our [ticketing site](https://openimis.atlassian.net/servicedesk/customer).

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Build Status](https://travis-ci.org/openimis/openimis-be_py.svg?branch=develop)](https://travis-ci.org/openimis/openimis-be_py)

## Developers setup

### To start working in openIMIS as a (module) developer:

<table align="center"><tr><td>When programming for openIMIS backend, you are highly encouraged to used the features provided in the openimis-be-core module. This includes (but is not limited to) date handling, user info,...</td></tr></table>

* clone this repo (creates the `openimis-be_py` directory)
* install python 3, recommended in a [virtualenv](https://virtualenv.pypa.io)
* install [pip](https://pip.pypa.io)
* within `openimis-be_py` directory
  * install openIMIS (external) dependencies: `pip install -r requirements.txt`
  * generate the openIMIS modules dependencies file (from openimis.json config): `python modules-requirements.py openimis.json > modules-requirements.txt`
  * install openIMIS current modules: `pip install -r modules-requirements.txt`
  * configure the database connection (see section here below)
* start openIMIS from within `openimis-be_py/openIMIS`: `python manage.py runserver`

At this stage, you may (depends on the database you connect to) need to:
* apply django migrations, from `openimis-be_py/openIMIS`: `python manage.py migrate`
* create a superuser for django admin console, from `openimis-be_py/openIMIS`: `python manage.py createsuperuser`

### To edit (modify) an existing openIMIS module (e.g. `openimis-be-claim`)
* checkout the module's git repo NEXT TO (not within!) `openimis-be_py` directory and create a git branch for your changes
* from `openimis-be_py`
  * uninstall the packaged module you want to work on (example: openimis-be-claim): `pip uninstall openimis-be-claim`
  * install the 'local' version of the module: `pip install -e ../openimis-be-claim_py/`
* from here on, openIMIS is using the local content of the module (with live update)

### To create a new openIMIS module (e.g. `openimis-be-mymodule`)
* create a (git-enabled) directory next to the other modules, with a subdirectory named as your module 'logical' name: `/openimis-be-mymodule_py/mymodule`
* from `/openimis-be_py/openIMIS`:
  * create the module skeleton: `python manage.py startapp mymodule ../../openimis-be-mymodule_py/mymodule/`
  * prepare your module to be mounted via pip: create and complete the `/openimis-be-mymodule_py/setup.py` (and README.md,... files)
  * every openIMIS module must provide its urlpatterns (even if empty):
    * create the file `/openimis-be-mymodule_py/mymodule/urls.py`
    * with content: `urlpatterns = []`
  * register your module in the pip requirements of openIMIS, referencing your 'local' codebase: `pip install -e ../../openimis-be-mymodule_py/`
  * register your module to openIMIS django site in `/openimis-be_py/openimis.json`
* from here on, your local openIMIS has a new module, directly loaded from your directory.

### To create a distinct implementation of an existing openIMIS module (e.g. `openimis-be-location-dhis2`)
* from `openimis-be_py`, uninstall the packaged module you want to replace: `pip uninstall openimis-be-location`
* follow the same procedure as for a brand new openIMIS module,
  ... but give it the same logical name as the one you want to replace: `/openimis-be-location-dhis2_py/location`

### To run unit tests on a module (example openimis-be-claim)
* from `openimis-be_py`
  * (re)initialize test database (at this stage structure is not managed by django): `python init_test_db.py`
  * launch unit tests, with the 'keep database' option: `python manage.py test -k claim`

### To publish (in PyPI) the modified (or new) module
* adapt the `openimis-be-mymodule_py/setup.py` to (at least) bump version number (e.g. 1.2.3)
* commit your changes to the git repo and merge into master
* tag the git repo according to your new version number:
  * `git tag -a v1.2.3 -m "v1.2.3"`
  * `git push --tags`
* create the PyPI package (can be automated on a ci-build): `python setup.py bdist_wheel`
* upload the created package (in `dist/`) to PyPI.org: `twine upload -r pypi dist/openimis_be_mymodule-1.2.3*`

## Distributor setup

Note: as a distributor, you may want to run an openIMIS version without docker. To do so, follow developers setup here above (up to running django migrations)

### To create an openIMIS Backend distribution
* clone this repo (creates the `openimis-be_py` directory) and create a git branch (named according to the release you want to bundle)
* adapt the `openimis-be_py/openimis.json` to specify the modules (and their versions) to be bundled
* make release candidates docker image from `openimis-be_py/`: `docker build . -t openimis-be-2.3.4`
* configure the database connection (see section here below)
* run the docker image, refering to environment variables file: `docker run --env-file .env openimis-be-2.3.4`
Note: when starting, the docker image will automatically apply the necessary database migrations to the database

When release candidate is accepted:
* commit your changes to the git repo
* tag the git repo according to your new version number
* upload openimis-be docker image to docker hub

Note:
This image only provides the openimis backend server.
The full openIMIS deployment (with the frontend,...) is managed from `openimis-dist_dkr` repo and its `docker-compose.yml` file.


## Database configuration (for developers and distributors)
The configuration for connection to the database is identical for developers and distributors:
* By default, openIMIS is connected to MS-SQL Server:
  * via ODBC (and pyodbc) driver
  * using TCP/IP protocol (with server DNS name as hostname... or localhost) and fixed port (leave `DB_PORT` here below empty for dynamic port)
  * SQL Server (not Windows/AD) authentication (user name password managed in SQL Server admin)
  Download and install the ODBC that correspond to your OS and MS-SQL Server version (https://docs.microsoft.com/en-us/sql/connect/odbc/)
* create a `openimis-be_py/.env` file to provide your database connection info:
  ```
  DB_HOST=mssql-host-server
  DB_PORT=mssql-port
  DB_NAME=database-name
  DB_USER=database-user
  DB_PASSWORD=database-password
  ```
Notes:
* instead of `.env` file, you can use environment variables (e.g. provided as parameters in the docker-compose.yml)
* default used django database 'engine' in openIMIS is `sql_server.pyodbc`.
  If you need to use anotherone, use the `DB_ENGINE` entry in the `.env` file
* default 'options' in openIMIS are `{'driver': 'ODBC Driver 17 for SQL Server','unicode_results': True}`
  If you need to provide other options, use the `DB_OPTIONS` entry in the `.env` file (be complete: the new json string will entirely replace the default one)  

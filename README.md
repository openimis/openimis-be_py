# openIMIS Backend Reference Implementation
This repository holds the configuration files for the openIMIS Backend Reference Implementation.
It serves 2 distinct use cases:
- developers who want to implement new modules or modify existing Backend modules of openIMIS
- distributors who want to assemble modules into a Docker image for delivery

This repo branches, tags,... are maintained by openIMIS official delivery team who use it to build the official openIMIS Docker images containing the official modules (versions) list.

## Developers setup

### To start working in openIMIS as a (module) developer:
* clone this repo (creates the `openimis-be_py` directory)
* install python 3, recommended in a [virtualenv](https://virtualenv.pypa.io)
* install [pip](https://pip.pypa.io)
* within `openimis-be_py` directory
  * install openIMIS (external) dependencies: `pip install -r requirements.txt`
  * generate the openIMIS modules dependencies file (from openimis.json config): `python modules-requirements.py openimis.json > modules-requirements`
  * install openIMIS current modules: `pip install -r modules-requirements.txt`
  * create a `openimis-be_py/.env` file to provide your database connection info (note: can also be passed in docker command line):
  ```
  DB_HOST=mssql-host-server
  DB_PORT=mssql-port
  DB_NAME=database-name
  DB_USER=database-user
  DB_PASSWORD=databaase-password
  ```
* start openIMIS from within `openimis-be_py/openIMIS`: `python manage.py runserver`

At this stage, you may (depends on the database you connect to) need to:
* apply django migrations, from `openimis-be_py/openIMIS`: `python manage.py migrate`
* create a superuser for django admin console, from `openimis-be_py/openIMIS`: `python manage.py createsuperuser`

### To start editing (modifying) an existing openIMIS module (e.g. `openimis-be-claim`)
* checkout the module's git repo NEXT TO (not within!) `openimis-be_py` directory and create a git branch for your changes
* from `openimis-be_py`
  * uninstall the packaged module you want to work on (example: openimis-be-claim): `pip uninstall openimis-be-claim`
  * install the 'local' version of the module: `pip install -e ../openimis-be-claim_py/`
* from here on, openIMIS is using the local content of the module (with live update)

### To publish (in PyPI) the modified module
* adapt the `openimis-be-claim_py/setup.py` to (at least) bump version number (e.g. 1.2.3)
* commit your changes to the git repo and merge into master
* tag the git repo according to your new version number
* create the PyPI package (can be automated on a ci-build): `python setup.py bdist_wheel`
* upload the created package (in `dist/`) to PyPI.org: `twine upload -r pypi dist/openimis_be_claim-1.2.3*`

## Distributor setup

### To create an openIMIS Backend distribution
* clone this repo (creates the `openimis-be_py` directory) and create a git branch (named according to the release you want to bundle)
* adapt the `openimis-be_py/openimis.json` to specify the modules (and their versions) to be bundled
* make release candidates docker image from `openimis-be_py/`: `docker build . -t openimis-be-2.3.4`
* create a `openimis-be_py/.env` file to provide your database connection info (note: can also be passed in docker command line):
  ```
  DB_HOST=mssql-host-server
  DB_PORT=mssql-port
  DB_NAME=database-name
  DB_USER=database-user
  DB_PASSWORD=databaase-password
  ```
* run the docker image, refering to environment variables file: `docker run --env-file .env openimis-be-2.3.4`
Note: when starting, the docker image will automatically apply the necessary database migrations to the database

When release candidate is accepted:
* commit your changes to the git repo
* tag the git repo according to your new version number
* upload openimis-be docker image to docker hub

Note:
This image only provides the openimis backend server.
The full openIMIS deployment (with the frontend,...) is managed from `openimis-dist_dck` repo and its `docker-compose.yml` file
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
  * install openIMIS (external) dependencies: `pip install -r
    requirements.txt`. For development workstations, one can use `pip
    install -r dev-requirements.txt` instead for more modules.
  * generate the openIMIS modules dependencies file (from openimis.json config): `python modules-requirements.py openimis.json > modules-requirements.txt`
  * install openIMIS current modules: `pip install -r modules-requirements.txt`
  * configure the database connection (see section here below)
* start openIMIS from within `openimis-be_py/openIMIS`: `python manage.py runserver`

At this stage, you may (depends on the database you connect to) need to:
* apply django migrations, from `openimis-be_py/openIMIS`: `python manage.py migrate`
* create a superuser for django admin console, from
  `openimis-be_py/openIMIS`: `python manage.py createsuperuser` (will
  not prompt for a password) and then `python manage.py changepassword
  <username>`

### To edit (modify) an existing openIMIS module (e.g. `openimis-be-claim`)
* checkout the module's git repo NEXT TO (not within!) `openimis-be_py` directory and create a git branch for your changes
* from `openimis-be_py`
  * uninstall the packaged module you want to work on (example: openimis-be-claim): `pip uninstall openimis-be-claim`
  * install the 'local' version of the module: `pip install -e ../openimis-be-claim_py/`
* from here on, openIMIS is using the local content of the module (with live update)

### To create a new openIMIS module (e.g. `openimis-be-mymodule`)
* create a (git-enabled) directory next to the other modules, with a subdirectory named as your module 'logical' name: `/openimis-be-mymodule_py/mymodule`
* from `/openimis-be_py/openIMIS`:
  * create the module skeleton: `python manage.py startapp mymodule ../../openimis-be-mymodule_py/mymodule`
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

### To manage translations of your module
* from your module root dir, execute '../openimis-be_py/gettext.sh'
  ... this extract all your translations keys from your code into your module root dir/locale/en/LC_MESSAGES/django.po
* you may want to provide translation in generated django.po file... or manage them via lokalize (need to upload the keys,...)

### To run unit tests on a module (example openimis-be-claim)
* from `openimis-be_py`
  * (re)initialize test database (at this stage structure is not managed by django): `python init_test_db.py`
  * launch unit tests, with the 'keep database' option: `python
    manage.py test --keep claim`

### To get profiler report (DEBUG mode only)
In request query include additional parameters:  
* `prof=True` - get profiler report instead of standard response for given endpoint
* `download=True` - additionally changes report formatting to one acceptable by `snakeviz` 

#### Example:   
`http://localhost:8000/api/graphql?prof=True&download=True`  
creates profiler report for execution of query/mutation defined in request's POST body.

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

### To create an openIMIS Backend distribution (Docker)
* clone this repo (creates the `openimis-be_py` directory) and create a git branch (named according to the release you want to bundle)
* adapt the `openimis-be_py/openimis.json` to specify the modules (and their versions) to be bundled
* make release candidates docker image from `openimis-be_py/`: `docker build . -t openimis-be-2.3.4`
* configure the database connection (see section here below)
* run the docker image, referring to environment variables file: `docker
  run --env-file .env openimis-be-2.3.4` Note: when starting, the docker
  image will automatically apply the necessary database migrations to
  the database

When release candidate is accepted:
* commit your changes to the git repo
* tag the git repo according to your new version number
* upload openimis-be docker image to docker hub

### To create an openIMIS Backend distribution (local)
* clone this repo (creates the `openimis-be_py` directory) and create a git branch (named according to the release you want to bundle)
* adapt the `openimis-be_py/openimis.json` to specify the modules (and their versions) to be bundled, the "pip" params can be:
	* standard pip: `openimis-be-core==1.2.0rc1`
	* from local: 	`-e ../openimis-be-core_py`
	* from git: `git+https://github.com/openimis/openimis-be-core_py.git@develop`
		- the egg can be specified so pip know what to look `git+https://github.com/openimis/openimis-be-core_py.git@develop#egg=openimis-be-core`
	* from tarball: `https://github.com/openimis/openimis-be_py/archive/v1.1.0.tar.gz`
* (required only once)`python -m venv ./venv`: create the python venv
* `./venv/Script/activate[.sh/.ps1]`: Activate the venv
* `pyhon modules-list.py openimis.json > module-list.txt`: list the module to install
* `python -m pip uninstall -r module-list.txt`: uninstall the previously installed module
* `pyhon modules-requirements.py openimis.json > modules-requirements.txt`: list the source of the module to install
* `python -m pip install -r modules-requirements.txt`: Install the modules
* Set the different required environement variables
	* see database configuration
	* SITE_ROOT: iapi for graphql, other  are possible in case there is multiple django backend serving the same urlpatterns
	* REMOTE_USER_AUTHENTICATION:  trust the header value "remote-user" for the user /!\ to be used ONLY behind a reverse proxy managing the authentification /!\
	* ROW_SECURITY: right based also on the location of the user
	* DEBUG: debug mode of django
	* OPENIMIS_CONF: path of the cofiguration file
* `python manage.py migrate`: execute the migrations
* `python manage.py runserver 0.0.0.0:PORT`: run the server



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
* default used django database 'engine' in openIMIS is
  `sql_server.pyodbc`. If you need to use another one, use the `DB_ENGINE` entry in the `.env` file
* default 'options' in openIMIS are `{'driver': 'ODBC Driver 17 for SQL Server','unicode_results': True}`
  If you need to provide other options, use the `DB_OPTIONS` entry in the `.env` file (be complete: the new json string will entirely replace the default one)




## Developer tools

### Adding Django Settings 
If modules are using additional libraries that would usually require changes in `settings.py`, 
these settings should be added within the module and not directly in assembly.  
To do this, `django_settings.py` file with `SETTINGS` variable containing 
a list of `SettingAttribute` objects has to be added to module (the same as in assembly module). 
`SettingAttribute` provides information regarding setting `name`, setting `value` and conflict `resolving policy`. 

#### Example: 
```python
# django_settings.py
from openIMIS.modulesettingsloader import SettingsAttribute, SettingsAttributeConflictPolicy as setting_type

SETTINGS = [
  SettingAttribute('CUSTOM_REQUIRED_SETTING', {'key': 'value'}, setting_type.MERGE_YIELD)
]
```
Is equivalent of assigning:
```python
# settings.py
CUSTOM_REQUIRED_SETTING = {'key': 'value'}
```
in `settings.py`.

Last parameter is used for resolving conflicts between overlying settings.  
By default, values are merged (dictionaries are combined, lists concatenated), and if it's not possible 
then already declared settings are not overridden.

### To create backend module skeleton in single command
* from `/openimis-be_py/openIMIS`:
  * run this command: `python manage.py create_openimis_module <module_name> <author> <author_email> [--template <template>]`
  * `<author>` and `<author_email>` params are required because they are necessary during creating `setup.py` file
  * `--template` param allow to specify a template adding additional files, depending on module type provided:
    * `business` template provides the module with `services.py` file containing example service, tests for that service, and 
    `apps.py` containing module config.
    * `calculation` template is an alias to `create_calcrule_module` command explained in `To create calculation backend
    module skeleton in single command` section
  * this command executes every steps described in "To create a new openIMIS module (e.g. `openimis-be-mymodule`)"
  * file templates for setup, readme, license, manifest and urls can be found in `developer_tools/skeletons` directory
  * files to be added through that command based on provided templates:
     * setup.py
     * README.md
     * LICENSE.md
     * MANIFEST.md
     * <module_name>/urls.py
  * as the option could be added `--github`. This allows to add gitignore file and workflows files to execute CI on every pull request (this option will execute this command `python manage.py add_github_files_to_module <module_name>`) 
  * example with using `--github` option: `python manage.py create_openimis_module <module_name> <author> <author_email> --github`
* from here on, your local openIMIS has a new module called `openimis-be-<module_name>_py`, directly loaded from your directory by using single command.


### To add GitHub files like workflows, gitignore etc
* from `/openimis-be_py/openIMIS`:
  * run this command: `python manage.py add_github_files_to_module <module_name>`
  * this command allows to add to the existing module github files like gitignore, workflows etc
  * files to be added through that command based on provided templates:
     * openmis-module-test.yml
     * python-publish.yml
     * .gitignore


### To fetch a module and install it from local directory
* first install all modules as in "Developers setup"
* from `/openimis-be_py/openIMIS`:
  * run this command: `python manage.py install_module_locally <module_name> [--url <url>] [--branch <branch>] [--path <path>]`.
  This command will execute all steps required steps to first uninstall currently installed version of the module, clone
  the module repository and install it as an editable library.
  * The `--url` parameter allows you to specify the git repository url (By default it will use openimis.json)
  * The `--branch` parameter allows to specify the branch that will be cloned, develop by default
  * The `--path` allows you to specify the directory the repository will be cloned to. By default, the repository will be saved
  next to `openimis-be_py` directory.
  

### To fetch all modules and install them from local directories
* first install all modules as in "Developers setup"
* from `/openimis-be_py/openIMIS`:
  * run this command: `python manage.py install_module_locally all`. This command will execute all steps required steps 
  to fetch all modules present in `openimis.json` from the git repositories and install them as editable libraries.


### To install modules from PyPI
* first install all modules as in "Developers setup"
* from `/openimis-be_py/openIMIS`:
  * run this command: `python manage.py install_module_pypi <module_name> [--target-version <version>] [--library-name <library_name>]
  [--check-only]`. This command will execute all steps required steps to first uninstall currently installed version of the module, check
  the newest version of the library and install it from PyPI.
  * The `--target-version` parameter allows you to specify the version that will be used to install the module
  * The `--library-name` parameter allows you to override the library name. By default, the library name is derived from
  module name, following this scheme: `openimis-be-<module_name>`
  * The `--check-only` flag allows to check the newest version without installing the library or modifying openimis.json
  file. This parameter can be also used to check availability of a specific version when used with `--target-version`


### To install all modules from PyPI
* first install all modules as in "Developers setup"
* from `/openimis-be_py/openIMIS`:
  * run this command: `python manage.py install_module_locally all`. This command will execute all steps required steps 
  to install most recent versions of all modules present in `openimis.json` from PyPI.

### To create calculation backend module skeleton in single command
* from `/openimis-be_py/openIMIS`:
  * run this command: `python manage.py create_calcrule_module <module_name> <author> <author_email>`
  * `<author>` and `<author_email>` params are required because they are necessary during creating `setup.py` file
  * file templates for apps.py, config.py and calculation_rule.py can be found in `developer_tools/skeletons` directory
  * another files necessary to launch module such as setup.py etc are also added by this command.  
  * files to be added through that command based on provided templates:
     * setup.py
     * README.md
     * LICENSE.md
     * MANIFEST.md
     * <module_name>/urls.py
     * <module_name>/apps.py
     * <module_name>/config.py
     * <module_name>/calculation_rule.py
  * as the option could be added `--github`. This allows to add gitignore file and workflows files so as to execute CI on every pull request (this option will execute this command `python manage.py add_github_files_to_module <module_name>`) 
  * example with using `--github` option: `python manage.py create_calcrule_module <module_name> <author> <author_email> --github`
* from here on, your local openIMIS has a new module called `openimis-be-calcrule-<module_name>_py`, directly loaded from your directory by using single command.

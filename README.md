# Environment Variables

| ENV | Values | Description |
| --------------------------- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| MODE | DEV, PROD | This is the mode of running the application. There are 2 modes available. DEV for the Development mode and PROD for the production mode. Certain settings will be changed according to the mode. Such as in the PROD mode, mutation will run asynchronously and synchronously otherwise. Same applies to DEBUG, it will be OFF in PROD and TRUE otherwise. |
| DB_ENGINE | django.db.backends.postgresql, mssql | Currently openIMIS supports 2 databases, as the values suggested, postgres and mssql. |
| DEMO_DATASET | true | Define if the database should be initiated with demo dataset. Comment for empty database. |
| DB_DEFAULT | String | String This variables sets the default database engine for the system. Possible values: postgresql, mssql. Default: postgresql. |
| DB_HOST | String | Define the name of your database server |
| DB_PORT | Integer | Define the port on which your database accepts the connection |
| DB_NAME | String | Define the name of the openIMIS database |
| DB_USER | String | Configure the username with which you want to connect to the database |
| DB_PASSWORD | String | Configure the database password |
| DB_TEST_NAME | String | If you are developing unit tests then this setting will create the testing database as per the name set|
| NO_DATABASE | true, false | If set to true, it will use sqlite.db3 as a database |
| DB_OPTIONS | String | Define any additional database options |
| PSQL_DB_ENGINE | String | Define a library to use to connect with postgres database. Default value is django.db.backends.postgresql |
| MSSQL_DB_ENGINE | String | Define a library to use to connect with MS SQL database Default value is mssql. |
| SITE_ROOT | String | Site root that will prefix all exposed endpoints. It's required when working with openIMIS frontend. For example, if the value is set `api` then the endpoint will appear like `your_domain_name/api/xxx` |
| DJANGO_LOG_LEVEL | INFO, WARNING, ERROR, DEBUG | Define the level of logs |
| DJANGO_LOG_HANDLER | console, debug-log | Depending on the value set, application will print the logs |
| DJANGO_DB_LOG_HANDLER | console, debug-log | Depending on the value set, application will print the logs |
| PHOTO_ROOT_PATH | String | Define the path for the photos of insurees. This setting is used in the Insuree module. The value set here will be overwritten by the InsureeConfig file. |
| DJANGO_MIGRATE | True, False | Based on the value set, application runs the migration command before starting up. If the SITE_ROOT value is set to api then the migration will always run regardless of the value |
| SCHEDULER_AUTOSTART | True, False | All the modules will be searched for the scheduled tasks, if the value is set to True |
| OPENSEARCH_HOSTS | String | Define the opensearch hosts, comma separated http://opensearch:9200 |
| OPENSEARCH_ADMIN | String | Define the login name for open search |
| OPENSEARCH_PASSWORD | String | Define the admin password to login to open search |
| BE_BRANCH | String | Define the github branch for the Backend form which you wan to install the module. Default is develop. |
| FE_BRANCH | String | Define the github branch for the Front-end form which you wan to install the module. Default is develop. |
| DB_BRANCH | String | Define the github branch for the Database form which you wan to install the module. Default is develop.| |
| LOKALISE_APIKEY | String | Set the lokalise api key. Obtain this key form the lokalise project to be able to use the lokalise-upload |
| OPENIMIS_CONF_JSON | String | Define the path for the openimis config file. If not set the default config from the root folder will be taken. |
| DB_QUERIES_LOG_FILE | String | Define the path of the file to save the database queries. Default is db-queries.log |
| DEBUG_LOG_FILE | String | Define the path of the file to save the debug log. Default is debug.log |
| SENTRY_DSN | String | Set the unique Sentry DSN. This can be obtained from your Sentry account dashboard |
| SENTRY_SAMPLE_RATE | 0-1 | This configuration allows you to to control the rate at which traces are collected. Values are between 0 and 1. 0 means no traces will be collected (tracing is disabled). 1 means traces will be collected for every request. Any value between 0 and 1 represents the probability of capturing trace. For instance, a value 0.3 means that approximately 30% of requests will have traces collected. |
| IS_SENTRY_ENABLED | True, False | Defines if the Sentry error tracking and monitoring functionality is enabled or disabled. |
| SITE_URL | String | Define the base url. This is used to create links in FHIR module |
| SITE_FRONT | String | Define base uri for the frontend|
| FRONTEND_URL | String | Define the frontend URL if not aligned with SITE_URL/SITE_FRONT|
| SECRET_KEY | String | This is used internally by Django. Make sure to set it up in production server. |
| REMOTE_USER_AUTHENTICATION | true, false | Set it to true if you want to enable the RemoteUserBackend as an authentication backend in Django. By default it's false |
| CELERY_BROKER_URL | String | Define a message broker url for celery. Default value is amqp://rabitmq |
| CHANNELS_HOST | String | Set the host for the Django Channel. Default value is amqp://guest:guest@127.0.0.1/ |
| EMAIL_HOST | String | Define an Email Host. Default value is localhost |
| EMAIL_PORT | Integer | Define a valid port for the email server |
| EMAIL_HOST_USER | String | Set the username to send emails |
| EMAIL_HOST_PASSWORD | String | Set the password for the email |
| EMAIL_USE_TLS | True, False | Configure the TLS setting. Default value is False |
| EMAIL_USE_SSL | True, False | Configure the SSL settings for the emails. Default value is False |
| DATA_UPLOAD_MAX_MEMORY_SIZE | Integer | Define the upload size allowed in **bytes** via the POST request. Default is 10 MB |
| MASTER_DATA_PASSWORD | String | This setting is used in exporting entities. Configure the password to zip the exported entities. |
| DJANGO_SETTINGS_MODULE | String | Define the python import path to settings module for Django project. By default it is set to openIMIS.settings |
| OPEHNHIM_URL | String | This setting is used in fhir module. Define the url for openHIM |
| OPEHNHIM_USER | String | This setting is used in fhir module. Define the user for openHIM |
| OPEHNHIM_PASSWORD | String | This setting is used in fhir module. Define the password for openHIM |
| OPENIMIS_CONF | String | Define a path to the config file. By default it reads from ../openimis.json|
| CLAIMDOC_TOKEN | String | Used in backend caching. Define a token to communicate with the remote server. Default is set to 'TestToken' |
| CACHE_BACKEND | String | Specifies the [caching backend](https://docs.djangoproject.com/en/5.0/topics/cache/#setting-up-the-cache) to be used. Default is set to PyMemcached. |
| CACHE_URL | String | Defines the location of the cache backend. Default is `unix:/tmp/memcached.sock` for a Unix socket connection. |
| CACHE_OPTIONS | String | A JSON string representing a dictionary of additional options passed to the cache backend. Empty by default |
| RATELIMIT_CACHE | String | The cache alias to use for rate limiting. Defaults to `default`. |
| RATELIMIT_KEY | String | Key to identify the client for rate limiting; `ip` means it will use the client's IP address. Defaults to `ip`. |
| RATELIMIT_RATE | String | Rate limit value (e.g., `150/m` for 150 requests per minute). Defaults to `150/m`. |
| RATELIMIT_METHOD | String | HTTP methods to rate limit; `ALL` means all methods. Defaults to `ALL`. |
| RATELIMIT_GROUP | String | Group name for the rate limit. Defaults to `graphql`. |
| RATELIMIT_SKIP_TIMEOUT | Boolean | Whether to skip rate limiting during cache timeout. Defaults to `False`. |
| HOSTS | String | Define the trusted domains that are used for PROD CORS and CSRF protection, separated by commas. Defaults to `localhost, 192.168.0.1`. |

## Developers setup

### To start working in openIMIS as a (module) developer:

When programming for openIMIS backend, you are highly encouraged to use the features provided in the openimis-be-core module. This includes (but is not limited to) date handling, user info,...

- clone this repo (creates the `openimis-be_py` directory)
- install python 3, recommended in a [venv](https://docs.python.org/3/library/venv.html) or [virtualenv](https://virtualenv.pypa.io)
- install [pip](https://pip.pypa.io)
- within `openimis-be_py` directory
  - install openIMIS (external) dependencies: `pip install -r requirements.txt`. For development workstations, one can use `pip install -r dev-requirements.txt` instead, for more modules.
  - In the script directory, 
    - generate the openIMIS modules dependencies file (from openimis.json config): `python modules-requirements.py ../openimis.json > modules-requirements.txt`
    - if you previously installed openIMIS on another version, it seems safe to uninstall all previous modules-requirement to be sure it match current version `pip uninstall -r modules-requirements.txt`
    - install openIMIS current modules: `pip install -r modules-requirements.txt`
  - Copy the example environment setup and adjust the settings (like database connection): `cp .env.example .env`.
    Refer to .env.example or the Environment Variable tables above for more info.
- start openIMIS from within `openimis-be_py/openIMIS`: `python manage.py runserver`

At this stage, you may (depends on the database you connect to) need to:

- apply django migrations, from `openimis-be_py/openIMIS`: `python manage.py migrate`
- create a superuser for django admin console, from
 `openimis-be_py/openIMIS`: `python manage.py createsuperuser` (will
 not prompt for a password) and then `python manage.py changepassword
<username>`

### To edit (modify) an existing openIMIS module (e.g. `openimis-be-claim`)

- checkout the module's git repo NEXT TO (not within!) `openimis-be_py` directory and create a git branch for your changes
- from `openimis-be_py`
 - uninstall the packaged module you want to work on (example: openimis-be-claim): `pip uninstall openimis-be-claim`
 - install the 'local' version of the module: `pip install -e ../openimis-be-claim_py/`
- from here on, openIMIS is using the local content of the module (with live update)

### To create a new openIMIS module (e.g. `openimis-be-mymodule`)

- create a (git-enabled) directory next to the other modules, with a subdirectory named as your module 'logical' name: `/openimis-be-mymodule_py/mymodule`
- from `/openimis-be_py/openIMIS`:
 - create the module skeleton: `python manage.py startapp mymodule ../../openimis-be-mymodule_py/mymodule`
 - prepare your module to be mounted via pip: create and complete the `/openimis-be-mymodule_py/setup.py` (and README.md,... files)
 - every openIMIS module must provide its urlpatterns (even if empty):
 - create the file `/openimis-be-mymodule_py/mymodule/urls.py`
 - with content: `urlpatterns = []`
 - register your module in the pip requirements of openIMIS, referencing your 'local' codebase: `pip install -e ../../openimis-be-mymodule_py/`
 - register your module to openIMIS django site in `/openimis-be_py/openimis.json`
- from here on, your local openIMIS has a new module, directly loaded from your directory.

### To create a distinct implementation of an existing openIMIS module (e.g. `openimis-be-location-dhis2`)

- from `openimis-be_py`, uninstall the packaged module you want to replace: `pip uninstall openimis-be-location`
- follow the same procedure as for a brand new openIMIS module,
 ... but give it the same logical name as the one you want to replace: `/openimis-be-location-dhis2_py/location`

### To manage translations of your module

- from your module root dir, execute '../openimis-be_py/script/gettext.sh'
 ... this extract all your translations keys from your code into your module root dir/locale/en/LC_MESSAGES/django.po
- you may want to provide translation in generated django.po file... or manage them via lokalize (need to upload the keys,...)

### To run unit tests on a module (example openimis-be-claim)

- from `openimis-be_py`
 - (re)initialize test database (at this stage structure is not managed by django):
 - launch unit tests, with the 'keep database' option: `python
manage.py test --keep claim`

### To get profiler report (DEBUG mode only)

In request query include additional parameters:

- `prof=True` - get profiler report instead of standard response for given endpoint
- `download=True` - additionally changes report formatting to one acceptable by `snakeviz`

#### Example:

`http://localhost:8000/api/graphql?prof=True&download=True` 
creates profiler report for execution of query/mutation defined in request's POST body.

### To publish (in PyPI) the modified (or new) module

- adapt the `openimis-be-mymodule_py/setup.py` to (at least) bump version number (e.g. 1.2.3)
- commit your changes to the git repo and merge into master
- tag the git repo according to your new version number:
 - `git tag -a v1.2.3 -m "v1.2.3"`
 - `git push --tags`
- create the PyPI package (can be automated on a ci-build): `python setup.py bdist_wheel`
- upload the created package (in `dist/`) to PyPI.org: `twine upload -r pypi dist/openimis_be_mymodule-1.2.3*`

## Distributor setup

Note: as a distributor, you may want to run an openIMIS version without docker. To do so, follow developers setup here above (up to running django migrations)

### To create an openIMIS Backend distribution (Docker)

- clone this repo (creates the `openimis-be_py` directory) and create a git branch (named according to the release you want to bundle)
- adapt the `openimis-be_py/openimis.json` to specify the modules (and their versions) to be bundled
- make release candidates docker image from `openimis-be_py/`: `docker build . -t openimis-be-2.3.4 [--build-arg="DB_DEFAULT=postgresql"]`
 - change the version (openimis-be-2.3.4) to the actual version you want to build
 - if only postgresql database is used, include the build-arg argument 
- configure the database connection (see section here below)
- run the docker image, referring to environment variables file: `docker run --env-file .env openimis-be-2.3.4` 
 Note: when starting, the docker image will automatically apply the necessary database migrations to
 the database

When release candidate is accepted:

- commit your changes to the git repo
- tag the git repo according to your new version number
- upload openimis-be docker image to docker hub

### To create an openIMIS Backend distribution (local)

- clone this repo (creates the `openimis-be_py` directory) and create a git branch (named according to the release you want to bundle)
- adapt the `openimis-be_py/openimis.json` to specify the modules (and their versions) to be bundled, the "pip" params can be:
 - standard pip: `openimis-be-core==1.2.0rc1`
 - from local: `-e ../openimis-be-core_py`
 - from git: `git+https://github.com/openimis/openimis-be-core_py.git@develop`
 - the egg can be specified so pip know what to look `git+https://github.com/openimis/openimis-be-core_py.git@develop#egg=openimis-be-core`
 - from tarball: `https://github.com/openimis/openimis-be_py/archive/v1.1.0.tar.gz`
- (required only once)`python -m venv ./venv`: create the python venv
- `./venv/Script/activate[.sh/.ps1]`: Activate the venv
- `python script/modules-requirements.py openimis.json > modules-requirements.txt`: list the source of the module to install
- `python -m pip install -r modules-requirements.txt`: Install the modules
- `cp .env.example .env`: Copy the example environment setup and adjust the variables (refer to .env.example for more info)
- `python manage.py migrate`: execute the migrations
- `python manage.py runserver 0.0.0.0:PORT`: run the server

## Database configuration (for developers and distributors)

The configuration for connection to the database is identical for developers and distributors:

- By default, openIMIS is connected to MS-SQL Server:
 - via ODBC (and pyodbc) driver
 - using TCP/IP protocol (with server DNS name as hostname... or localhost) and fixed port (leave `DB_PORT` here below empty for dynamic port)
 - SQL Server (not Windows/AD) authentication (user name password managed in SQL Server admin)
 Download and install the ODBC that correspond to your OS and MS-SQL Server version (https://docs.microsoft.com/en-us/sql/connect/odbc/)
- Copy the example environment setup and adjust the variables: `cp .env.example .env`. Refer to .env.example for more info.
 ```
 DB_HOST=mssql-host-server
 DB_PORT=mssql-port
 DB_NAME=database-name
 DB_USER=database-user
 DB_PASSWORD=database-password
 ```
 Notes:
- instead of `.env` file, you can use environment variables (e.g. provided as parameters in the docker-compose.yml)
- default used django database 'engine' in openIMIS is
 `sql_server.pyodbc`. If you need to use another one, use the `DB_ENGINE` entry in the `.env` file
- default 'options' in openIMIS are `{'driver': 'ODBC Driver 17 for SQL Server','unicode_results': True}`
 If you need to provide other options, use the `DB_OPTIONS` entry in the `.env` file (be complete: the new json string will entirely replace the default one)

## Developer tools

### To create backend module skeleton in single command

- from `/openimis-be_py/openIMIS`:
 - run this command: `python manage.py create_openimis_module <module_name> <author> <author_email> [--template <template>]`
 - `<author>` and `<author_email>` params are required because they are necessary during creating `setup.py` file
 - `--template` param allow to specify a template adding additional files, depending on module type provided: - `business` template provides the module with `services.py` file containing example service, tests for that service, and
 `apps.py` containing module config. - `calculation` template is an alias to `create_calcrule_module` command explained in `To create calculation backend
module skeleton in single command` section
 - this command executes every steps described in "To create a new openIMIS module (e.g. `openimis-be-mymodule`)"
 - file templates for setup, readme, license, manifest and urls can be found in `developer_tools/skeletons` directory
 - files to be added through that command based on provided templates:
 - setup.py
 - README.md
 - LICENSE.md
 - MANIFEST.md
 - <module_name>/urls.py
 - as the option could be added `--github`. This allows to add gitignore file and workflows files to execute CI on every pull request (this option will execute this command `python manage.py add_github_files_to_module <module_name>`)
 - example with using `--github` option: `python manage.py create_openimis_module <module_name> <author> <author_email> --github`
- from here on, your local openIMIS has a new module called `openimis-be-<module_name>_py`, directly loaded from your directory by using single command.

### To add GitHub files like workflows, gitignore etc

- from `/openimis-be_py/openIMIS`:
 - run this command: `python manage.py add_github_files_to_module <module_name>`
 - this command allows to add to the existing module github files like gitignore, workflows etc
 - files to be added through that command based on provided templates:
 - openmis-module-test.yml
 - python-publish.yml
 - .gitignore

### To fetch a module and install it from local directory

- first install all modules as in "Developers setup"
- from `/openimis-be_py/openIMIS`:
 - run this command: `python manage.py install_module_locally <module_name> [--url <url>] [--branch <branch>] [--path <path>]`.
 This command will execute all steps required steps to first uninstall currently installed version of the module, clone
 the module repository and install it as an editable library.
 - The `--url` parameter allows you to specify the git repository url (By default it will use openimis.json)
 - The `--branch` parameter allows to specify the branch that will be cloned, develop by default
 - The `--path` allows you to specify the directory the repository will be cloned to. By default, the repository will be saved
 next to `openimis-be_py` directory.

### To fetch all modules and install them from local directories

- first install all modules as in "Developers setup"
- from `/openimis-be_py/openIMIS`:
 - run this command: `python manage.py install_module_locally all`. This command will execute all steps required steps
 to fetch all modules present in `openimis.json` from the git repositories and install them as editable libraries.

### To install modules from PyPI

- first install all modules as in "Developers setup"
- from `/openimis-be_py/openIMIS`:
 - run this command: `python manage.py install_module_pypi <module_name> [--target-version <version>] [--library-name <library_name>]
[--check-only]`. This command will execute all steps required steps to first uninstall currently installed version of the module, check
 the newest version of the library and install it from PyPI.
 - The `--target-version` parameter allows you to specify the version that will be used to install the module
 - The `--library-name` parameter allows you to override the library name. By default, the library name is derived from
 module name, following this scheme: `openimis-be-<module_name>`
 - The `--check-only` flag allows to check the newest version without installing the library or modifying openimis.json
 file. This parameter can be also used to check availability of a specific version when used with `--target-version`

### To install all modules from PyPI

- first install all modules as in "Developers setup"
- from `/openimis-be_py/openIMIS`:
 - run this command: `python manage.py install_module_locally all`. This command will execute all steps required steps
 to install most recent versions of all modules present in `openimis.json` from PyPI.

### To create calculation backend module skeleton in single command

- from `/openimis-be_py/openIMIS`:
 - run this command: `python manage.py create_calcrule_module <module_name> <author> <author_email>`
 - `<author>` and `<author_email>` params are required because they are necessary during creating `setup.py` file
 - file templates for apps.py, config.py and calculation_rule.py can be found in `developer_tools/skeletons` directory
 - another files necessary to launch module such as setup.py etc are also added by this command.
 - files to be added through that command based on provided templates:
 - setup.py
 - README.md
 - LICENSE.md
 - MANIFEST.md
 - <module_name>/urls.py
 - <module_name>/apps.py
 - <module_name>/config.py
 - <module_name>/calculation_rule.py
 - as the option could be added `--github`. This allows to add gitignore file and workflows files so as to execute CI on every pull request (this option will execute this command `python manage.py add_github_files_to_module <module_name>`)
 - example with using `--github` option: `python manage.py create_calcrule_module <module_name> <author> <author_email> --github`
- from here on, your local openIMIS has a new module called `openimis-be-calcrule-<module_name>_py`, directly loaded from your directory by using single command.

### To create release branches for all backend/frontend modules presented in openimis.json

- from `/openimis-be_py/openIMIS`:
 - run this command: `python manage.py create_release_branch <version> <from_branch: by default 'develop'>`. This command will execute all steps required
 to create release branches of all modules present in `openimis.json` (frontend json and backend json).

### To extract all translations from frontend modules

- from `/openimis-be_py/openIMIS`:
 - run this command: `python manage.py extract_translations`. This command will execute all steps required
 to extract frontend translations of all modules present in `openimis.json`.
 - those translations will be copied into 'extracted_translations_fe' folder in assembly backend module

### JWT Security Configuration

To enhance JWT token security, you can configure the system to use RSA keys for signing and verifying tokens.

1. **Generate RSA Keys**:
 ```bash
 # Generate a private key
 openssl genpkey -algorithm RSA -out jwt_private_key.pem -aes256

 # Generate a public key
 openssl rsa -pubout -in jwt_private_key.pem -out jwt_public_key.pem

2. **Store RSA Keys**:
 Place jwt_private_key.pem and jwt_public_key.pem in a secure directory within your project, e.g., keys/.

3. **Django Configuration**:
 Ensure that the settings.py file is configured to read these keys. If RSA keys are found, the system will use RS256. Otherwise, it will fallback to HS256 using DJANGO_SECRET_KEY.

Note: If RSA keys are not provided, the system defaults to HS256. Using RS256 with RSA keys is recommended for enhanced security.


## CSRF Setup Guide

CSRF (Cross-Site Request Forgery) protection ensures that unauthorized commands are not performed on behalf of authenticated users without their consent. It achieves this by including a unique token in each form submission or AJAX request, which is then validated by the server.
When using JWT (JSON Web Token) for authentication, CSRF protection is not executed because the server does not rely on cookies for authentication. Instead, the JWT is included in the request headers, making CSRF attacks less likely.

### Development Environment

In the development environment, CSRF protection is configured to allow requests from `localhost:3000` and `localhost:8000` by default in .env.example file.

### Production Environment

In the production environment, you need to specify the trusted origins in your `.env` file.

1. **Trusted Origins Setup**:
 - Define the trusted origins in your `.env` file to allow cross-origin requests from specific domains.
 - Use a comma-separated list to specify multiple origins.
 - Example of setting trusted origins in `.env`:
 ```env
 CSRF_TRUSTED_ORIGINS=https://example.com,https://api.example.com
 ```


## Security Headers

This section describes the security headers used in the application, based on OWASP recommendations, to enhance the security of your Django application.

### Security Headers in Production

In the production environment, several security headers are set to protect the application from common vulnerabilities:

- **Strict-Transport-Security**: `max-age=63072000; includeSubDomains` - Enforces secure (HTTP over SSL/TLS) connections to the server and ensures all subdomains also follow this rule.
- **Content-Security-Policy**: `default-src 'self';` - Prevents a wide range of attacks, including Cross-Site Scripting (XSS), by restricting sources of content to the same origin.
- **X-Frame-Options**: `DENY` - Protects against clickjacking attacks by preventing the page from being framed.
- **X-Content-Type-Options**: `nosniff` - Prevents the browser from MIME-sniffing the content type, ensuring that the browser uses the declared content type.
- **Referrer-Policy**: `no-referrer` - Controls how much referrer information is included with requests by not sending any referrer information with requests.
- **Permissions-Policy**: `geolocation=(), microphone=()` - Controls access to browser features by disabling access to geolocation and microphone features.

In production, additional security settings are applied to cookies used for CSRF and JWT:

- **CSRF_COOKIE_SECURE**: Ensures the CSRF cookie is only sent over HTTPS.
- **CSRF_COOKIE_HTTPONLY**: Prevents JavaScript from accessing the CSRF cookie.
- **CSRF_COOKIE_SAMESITE**: Sets the `SameSite` attribute to 'Lax', which allows the cookie to be sent with top-level navigations and gets rid of the risk of CSRF attacks.
- **JWT_COOKIE_SECURE**: Ensures the JWT cookie is only sent over HTTPS.
- **JWT_COOKIE_SAMESITE**: Sets the `SameSite` attribute to 'Lax' for the JWT cookie.


## Custom exception handler for new modules REST-based modules

If the module you want to add to the openIMIS uses its own REST exception handler you have to register
it in the main module. To do this, you can use following code snippet in the class
`ModuleConfig` (in your `apps.py` file). Add this in the `def ready(self)` method:

```Python
from openIMIS.ExceptionHandlerRegistry import ExceptionHandlerRegistry
from .exceptions.your_exception_handler import your_exception_handler
ExceptionHandlerRegistry.register_exception_handler(MODULE_NAME, your_exception_handler)
```

This way, the exception handler in the main module will check if incoming rest request has to be handled
by specific code in the added module. If not - default DRF handler will take care of that.

## Handling errors while running openIMIS app - the most common ones

### Handling error with `wheel` package

If there are some problems with 'wheel package' after executing `pip install -r requirements.txt` (for example `error: invalid command 'bdist_wheel'`) you may need to execute two commands:

- `pip install wheel`
- `python setup.py bdist_wheel`
- optionally `pip uninstall -r requirements.txt` to clean requirements and reinstall them again

If those commands doesn't help you need to try with this sort of commands:

- `apt-get update`
- `ACCEPT_EULA=Y apt-get install -y msodbcsql17 mssql-tools`
- `apt-get install -y -f python3-dev unixodbc-dev`
- `pip install --upgrade pip`
- `pip install mssql-cli`

After executing those commands you can run `pip install -r requirements.txt` again and there shouldn't be any issues with `wheel` package.

### Handling error with `connection_is_mariadb` after executing `python manage.py runserver`

Another error that relates to this issue with `wheel` is such one:

- `ImportError: cannot import name 'connection_is_mariadb' from 'django_mysql.utils'`
 This error indicates that the db client is not set up properly. But it realized that it is related to the fact that the wheel package is not working (see `### Handling error with wheel package` section).
 Therefore you need to follows steps described in this above section.

### Using wrong build for database docker

Using wrong version of db docker could cause several issues both on backend and frontend for example:

- problems with creating database schema (backend)
- problems with filling demo dataset into database while running demo database script (backend)
- error while running frontend (web console `Uncaught TypeError: Cannot read properties of null (reading 'health_facility_id')`) (frontend)

So as to avoid those issues it is recommended to use such command to run db docker (NOTE: DO NOT USE for a production environment!):

```
docker build \
 --build-arg ACCEPT_EULA=Y \
 --build-arg SA_PASSWORD=<your secret password> \
 . \
 -t openimis-db
```

This commands will build with the latest version of database. You can specify particular version of database by adding optional parameter:

- `SQL_SCRIPT_URL=<url to the sql script to create the database>`

You can find more informations about seeting up db docker [here](https://github.com/openimis/openimis-db_dkr/tree/develop).

### How to report another issues?

If you face another issues not described in that section you could use our [ticketing site](https://openimis.atlassian.net/servicedesk/customer/portal/1).
Here you can report any bugs/problems you faced during setting up openIMIS app.

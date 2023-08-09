# assuming venv and openimis-be_py folders are on the same level
..\venv\Scripts\Activate.ps1
cd openIMIS
$SITE_ROOT='iapi'
$DB_NAME='IMISfs'
$DB_USER='IMISuser'
$DB_PASSWORD='IMISuser@1234'
$DB_HOST='127.0.0.1'
$DB_PORT='1433'
$DJANGO_PORT='8000'
[Environment]::SetEnvironmentVariable("SITE_ROOT", $SITE_ROOT)
[Environment]::SetEnvironmentVariable("REMOTE_USER_AUTHENTICATION", "False")
[Environment]::SetEnvironmentVariable("ROW_SECURITY", "False")
[Environment]::SetEnvironmentVariable("DEBUG", "True")
[Environment]::SetEnvironmentVariable("DB_NAME", $DB_NAME)
[Environment]::SetEnvironmentVariable("DB_USER", $DB_USER)
[Environment]::SetEnvironmentVariable("DB_PASSWORD", $DB_PASSWORD)
[Environment]::SetEnvironmentVariable("DB_HOST", $DB_HOST)
[Environment]::SetEnvironmentVariable("DB_PORT", $DB_PORT)
[Environment]::SetEnvironmentVariable("DJANGO_PORT", $DJANGO_PORT)
[Environment]::SetEnvironmentVariable("OPENIMIS_CONF", "../"$OPENIMIS_CONF)
python manage.py runserver
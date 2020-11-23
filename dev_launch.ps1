# assuming venv and openimis-be_py folders are on the same level
..\venv\Scripts\Activate.ps1
cd openIMIS
[Environment]::SetEnvironmentVariable("SITE_ROOT", "api")
[Environment]::SetEnvironmentVariable("REMOTE_USER_AUTHENTICATION", "True")
[Environment]::SetEnvironmentVariable("ROW_SECURITY", "False")
[Environment]::SetEnvironmentVariable("DEBUG", "True")
python manage.py runserver
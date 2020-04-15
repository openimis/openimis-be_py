param(
[string]$mode,
[string]$REMOTE='',
[string]$PORT=1433,
[string]$WAIT=5
)
  




function  show_help{
  Write-Output """
  Commands
  ---------------------------------------------------------------

  start            : start django
  worker           : start Celery worker

  manage           : run django manage.py
  eval             : eval shell command
  bash             : run bash
  """
}

#export PYTHONPATH="/opt/app:$PYTHONPATH"
if (!(Test-Path 'env:DJANGO_SETTINGS_MODULE')) { 
    [Environment]::SetEnvironmentVariable("DJANGO_SETTINGS_MODULE ", "openIMIS.settings", "User")
}

Switch  ($mode) {
  "start" {
	While (![string]::IsNullOrEmpty($REMOTE)){
		 if((Test-NetConnection -ComputerName  $REMOTE -Port $PORT -InformationLevel Quiet)  -eq "error"){
			break;
		 }else{
			Write-output "Test Connection to $REMOTE failed, waiting for $WAIT seconds"
			Start-Sleep -Seconds $WAIT;
		 }
	}
    Write-Output "Migrating..."
	Start-Sleep -Seconds $WAIT;
    python manage.py migrate
    Write-Output "Starting Django..."
    python server.py
  }
  "worker" {
    Write-Output "Starting Celery with url ${CELERY_BROKER_URL} ${DB_NAME}..."
    Write-Output "Settings module: $DJANGO_SETTINGS_MODULE"
    celery -A openIMIS worker --loglevel=DEBUG
  }
  "manage" {
    python ./manage.py "${@:2}"
  }
  "eval" {
    Invoke-Expression "${@:2}"
  }
  "bash" {
    powershell -noexit
  }
  default {
    show_help
  }
}


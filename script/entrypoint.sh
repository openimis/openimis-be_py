#!/bin/bash
set -e



install_modules() {
    # Create and activate shared venv if not exists
    if [ ! -d /venv/bin ]; then
      python -m venv /venv
    fi
    source /venv/bin/activate
    local config_file=$1
    local config_name=$(basename "$config_file" .json)
    local req_file="modules-requirements-${config_name}.txt"

    echo "Installing modules for $config_file..."

    # Generate requirements (always do this to ensure we have latest)
    python ./modules-requirements.py "$config_file" > "$req_file"

    # Always install modules but use pip cache to avoid re-downloading
    echo "Installing modules (using cache for dependencies)..."
    pip install --quiet --cache-dir /pip-cache -r "$req_file"

    echo "Module installation complete."
}

show_help() {
  echo """
  Commands
  ---------------------------------------------------------------

  start            : start django
  worker           : start Celery worker
  start_asgi       : use daphne -b ASGI_IP:WSGI_PORT -p SERVER_PORT  ASGI_APPLICATION
  start_wsgi       : use gunicorn -b WSGI_IP:WSGI_PORT -w WSGI_WORKERS WSGI_APPLICATION
  manage           : run django manage.py
  eval             : eval shell command
  bash             : run bash
  init             : initialize database
  """
}

init(){
  cd /openimis-be/openIMIS
  echo "=== Applying migrations ==="
    python manage.py migrate --no-input || {
        code=$?
        if [ $code -eq 5 ]; then
            echo "migrate exited with code 5 (unapplied model changes) – continuing..."
        else
            echo "migrate failed with code $code"
            exit $code
        fi
    }

    echo "=== Loading fixtures ==="
    if [ -n "${FIXTURE_SOLUTION:-}" ]; then
        python manage.py load_fixtures --solution "$FIXTURE_SOLUTION"
    else
        python manage.py load_fixtures
    fi

    export SCHEDULER_AUTOSTART=True
    echo "=== Initialization complete ==="
}

#export PYTHONPATH="/opt/app:$PYTHONPATH"
if [ -z "$DJANGO_SETTINGS_MODULE" ]; then
  export DJANGO_SETTINGS_MODULE=openIMIS.settings
fi

case "$1" in
  "dev" )
    echo "Starting Django in development mode..."
    install_modules "../openimis-dev.json"
    cd /openimis-be/openIMIS
    OPENIMIS_CONF=../openimis-dev.json python server.py
  ;;
  "debug" )
    echo "Starting Django in debug mode..."
    install_modules "../openimis-dev.json"
    cd /openimis-be/openIMIS
    OPENIMIS_CONF=../openimis-dev.json python -m debugpy --listen 0.0.0.0:5678 --wait-for-client manage.py runserver 0.0.0.0:8000 --noreload --nothreading
  ;;
  "start" )
    echo "Starting Django in production mode..."
    # In production, modules should already be installed during build
    # But add a safety check in case they're not
    if ! python -c "import sys; sys.path.insert(0, 'openIMIS'); from openimisconf import load_openimis_conf; print('Modules OK')" 2>/dev/null; then
        echo "Installing production modules..."
        install_modules "openimis.json"
    fi
    cd /openimis-be/openIMIS
    python server.py
  ;;
  "start_asgi" )
    echo "Starting Django ASGI..."
    def_ip='0.0.0.0'
    def_port='8000'
    def_app='openIMIS.asgi:application'

    SERVER_IP="${ASGI_IP:-$def_ip}"
    SERVER_PORT="${ASGI_PORT:-$def_port}"
    SERVER_APPLICATION="${ASGI_APPLICATION:-$def_app}"

    daphne -b "$SERVER_IP" -p "$SERVER_PORT" "$SERVER_APPLICATION"
  ;;
  "init" )
    init
    exit 0
  ;;
  "init-dev" )
    echo "Migrating Django in debug mode..."
    install_modules "../openimis-dev.json"
    init
    exit 0
  ;;
  "start_wsgi" )
    echo "Starting Django WSGI..."
    def_ip='0.0.0.0'
    def_port='8000'
    def_app='openIMIS.wsgi'

    SERVER_IP="${WSGI_IP:-$def_ip}"
    SERVER_PORT="${WSGI_PORT:-$def_port}"
    SERVER_APPLICATION="${WSGI_APPLICATION:-$def_app}"
    SERVER_WORKERS="${WSGI_WORKERS:-4}"

    gunicorn -b "$SERVER_IP:$SERVER_PORT" -w $SERVER_WORKERS "$SERVER_APPLICATION"
  ;;
  "worker" )
    echo "Starting Celery with url ${CELERY_BROKER_URL} ${DB_NAME}..."
    echo "Settings module: $DJANGO_SETTINGS_MODULE"
    celery -A openIMIS worker --loglevel=DEBUG
  ;;
  "manage" )
    ./manage.py "${@:2}"
  ;;
  "eval" )
    eval "${@:2}"
  ;;
  "bash" )
    bash
  ;;
  * )
    show_help
  ;;
esac

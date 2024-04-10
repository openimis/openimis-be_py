FROM python:3.10-buster As builder
ENV PYTHONUNBUFFERED 1
ARG DB_ENGINE
ENV DB_ENGINE=${DB_ENGINE:-mssql}
RUN apt-get update && apt-get install -y apt-transport-https ca-certificates gettext unixodbc-dev && apt-get upgrade -y
RUN apt-get install -y -f python3-dev
RUN apt-get -y install git

RUN test "$DB_ENGINE" != "django.db.backends.postgresql" && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - || :
RUN test "$DB_ENGINE" != "django.db.backends.postgresql" && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list || :
RUN test "$DB_ENGINE" != "django.db.backends.postgresql" && apt-get update || :
RUN test "$DB_ENGINE" != "django.db.backends.postgresql" && ACCEPT_EULA=Y apt-get install -y msodbcsql17 mssql-tools || :

RUN pip install --upgrade pip
RUN test "$DB_ENGINE" != "django.db.backends.postgresql" && pip install mssql-cli || :

RUN pip install gunicorn

FROM builder As app

# Install requirements
COPY requirements.txt /.
RUN pip install -r requirements.txt

ARG SENTRY_DSN
RUN test -z "$SENTRY_DSN" || pip install -r sentry-requirements.txt && :

RUN mkdir /openimis-be
COPY . /openimis-be
WORKDIR /openimis-be

ARG OPENIMIS_CONF_JSON
ENV OPENIMIS_CONF_JSON=${OPENIMIS_CONF_JSON}
RUN python modules-requirements.py openimis.json > modules-requirements.txt && pip install -r modules-requirements.txt 

WORKDIR /openimis-be/openIMIS

# Compile messages (Exclude zh_Hans)
RUN NO_DATABASE=True python manage.py compilemessages -x zh_Hans
RUN NO_DATABASE=True python manage.py collectstatic --clear --noinput

ENTRYPOINT ["/openimis-be/script/entrypoint.sh"]

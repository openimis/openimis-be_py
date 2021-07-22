FROM python:3.8-buster
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y apt-transport-https ca-certificates gettext
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql17 mssql-tools 
RUN apt-get install -y python3-dev unixodbc-dev 
RUN pip install --upgrade pip
RUN mkdir /openimis-be
COPY . /openimis-be
COPY ${OPENIMIS_CONF_JSON} ./openimis_local.json
WORKDIR /openimis-be
RUN pip install mssql-cli
RUN pip install -r requirements.txt
RUN python modules-requirements.py openimis.json > modules-requirements.txt
RUN pip install -r modules-requirements.txt
WORKDIR /openimis-be/openIMIS
RUN NO_DATABASE=True python manage.py compilemessages
RUN NO_DATABASE=True python manage.py collectstatic --clear --noinput
ENTRYPOINT ["/openimis-be/script/entrypoint.sh"]
# CMD ["/openimis-be/script/entrypoint.sh"]

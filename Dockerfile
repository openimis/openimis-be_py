FROM python:3.7-stretch
ENV PYTHONUNBUFFERED 1
ENV REMOTE_USER_AUTHENTICATION false
ENV ROW_SECURITY true
ENV DEBUG false
RUN apt-get update && apt-get install -y apt-transport-https ca-certificates gettext
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql17 mssql-tools mssql-cli
RUN apt-get install -y python3-dev unixodbc-dev
RUN pip install --upgrade pip
RUN mkdir /openimis-be-claim_py
RUN mkdir /openimis-be-calculation_py
RUN mkdir /openimis-be-contract_py
RUN mkdir /openimis-be-contribution_plan_py
RUN mkdir /openimis-be-policyholder_py
RUN mkdir /openimis-be-api_fhir_r4_py

RUN mkdir /openimis-be-core_py

RUN mkdir /openimis-be-claim_ai_quality_py
RUN mkdir /openimis-be-claim_ai_py

COPY ./openimis-be-claim_py /openimis-be-claim_py
COPY ./openimis-be-calculation_py /openimis-be-calculation_py
COPY ./openimis-be-contract_py /openimis-be-contract_py
COPY ./openimis-be-contribution_plan_py /openimis-be-contribution_plan_py
COPY ./openimis-be-policyholder_py /openimis-be-policyholder_py
COPY ./IMIS_AI_PROJECT/openimis-be-api_fhir_r4_py /openimis-be-api_fhir_r4_py

COPY ./openimis-be_py /openimis-be
COPY ./openimis-be-core_py /openimis-be-core_py
COPY ./openimis-be-claim_ai_quality_py /openimis-be-claim_ai_quality_py
COPY ./openimis-be-claim_ai_py /openimis-be-claim_ai_py

WORKDIR /openimis-be
RUN pip install -r requirements.txt
RUN python modules-requirements.py openimis.json > modules-requirements.txt
RUN pip install -r modules-requirements.txt
WORKDIR /openimis-be/openIMIS
RUN NO_DATABASE=True python manage.py compilemessages
RUN NO_DATABASE=True python manage.py collectstatic --clear --noinput
ENTRYPOINT ["/openimis-be/script/entrypoint.sh"]
# CMD ["/openimis-be/script/entrypoint.sh"]

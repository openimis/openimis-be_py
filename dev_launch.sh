#!/bin/bash
source venv/bin/activate
pip install -r requirements.txt 
python modules-requirements.py openimis.json > modules-requirements.txt 
pip install -r modules-requirements.txt 
cd openIMIS
python mnanage.py migrate
SITE_ROOT=api REMOTE_USER_AUTHENTICATION=False ROW_SECURITY=False DEBUG=True python manage.py runserver

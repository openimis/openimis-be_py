#!/bin/bash
source venv/bin/activate
cd openIMIS
SITE_ROOT=api REMOTE_USER_AUTHENTICATION=True DEBUG=True python manage.py runserver
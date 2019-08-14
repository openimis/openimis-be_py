#!/bin/bash
source venv/bin/activate
cd openIMIS
SITE_ROOT=api REMOTE_USER_AUTHENTICATION=True DEBUG=True ROW_SECURITY=False python manage.py runserver
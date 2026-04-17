# settings/dev.py
import os

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
ALLOWED_HOSTS = ['*']
#Disable CRSF for DEV
MIDDLEWARE = [m for m in MIDDLEWARE if 'csrf' not in m]  # remove entirely

# CORS: allow all
def cors_allow_origin(origin):
    return True
CORS_ALLOWED_ORIGINS = []
CORS_ALLOWED_ORIGIN_REGEXES = []
CORS_ORIGIN_WHITELIST_FUNC = cors_allow_origin  # ← correct name
CORS_ALLOW_CREDENTIALS = True

# Dev cookies
CSRF_COOKIE_SECURE = False
CSRF_TRUSTED_ORIGINS = ["http://localhost:8000","http://localhost:3000"]
SESSION_COOKIE_SECURE = False
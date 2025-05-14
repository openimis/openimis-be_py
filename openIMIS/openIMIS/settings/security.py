import os
from .common import DEBUG, BASE_DIR
from datetime import timedelta
from cryptography.hazmat.primitives import serialization


AUTH_USER_MODEL = "core.User"

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

if not DEBUG:
    AUTH_PASSWORD_VALIDATORS = [
        {
            "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        },
        {
            "NAME": "core.utils.CustomPasswordValidator",
        }
    ]

# SECURITY WARNING: don't run without row security in production!
# Row security is dedicated to filter the data result sets according to users' right
# Example: user registered at a Health Facility should only see claims recorded for that Health Facility
ROW_SECURITY = os.environ.get("ROW_SECURITY", "True").lower() == "true"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "SECRET_KEY", "chv^^7i_v3-04!rzu&qe#+h*a=%h(ib#5w9n$!f2q7%2$qp=zz"
)
REMOTE_USER_AUTHENTICATION = os.environ.get("REMOTE_USER_AUTHENTICATION", "false").lower() == "true"


GRAPHQL_JWT = {
    "JWT_VERIFY_EXPIRATION": True,
    "JWT_EXPIRATION_DELTA": timedelta(days=1),
    "JWT_REFRESH_EXPIRATION_DELTA": timedelta(days=30),
    "JWT_AUTH_HEADER_PREFIX": "Bearer",
    "JWT_ENCODE_HANDLER": "core.jwt.jwt_encode_user_key",
    "JWT_DECODE_HANDLER": "core.jwt.jwt_decode_user_key",
    # This can be used to expose some resources without authentication
    "JWT_ALLOW_ANY_CLASSES": [
        "graphql_jwt.mutations.ObtainJSONWebToken",
        "graphql_jwt.mutations.Verify",
        "graphql_jwt.mutations.Refresh",
        "graphql_jwt.mutations.Revoke",
        "core.schema.ResetPasswordMutation",
        "core.schema.SetPasswordMutation",
    ],
}

# Load RSA keys
private_key_path = os.path.join(BASE_DIR, 'keys', 'jwt_private_key.pem')
public_key_path = os.path.join(BASE_DIR, 'keys', 'jwt_public_key.pem')

if os.path.exists(private_key_path) and os.path.exists(public_key_path):
    with open(private_key_path, 'rb') as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None,
        )

    with open(public_key_path, 'rb') as f:
        public_key = serialization.load_pem_public_key(
            f.read(),
        )

    # If RSA keys exist, update the algorithm and add keys to GRAPHQL_JWT settings
    GRAPHQL_JWT.update({
        "JWT_ALGORITHM": "RS256",
        "JWT_PRIVATE_KEY": private_key,
        "JWT_PUBLIC_KEY": public_key,
    })


# Lockout mechanism configuration
AXES_FAILURE_LIMIT = int(os.getenv("LOGIN_LOCKOUT_FAILURE_LIMIT", 5))
AXES_COOLOFF_TIME = timedelta(minutes=int(os.getenv("LOGIN_LOCKOUT_COOLOFF_TIME", 5)))
AXES_ENABLED = True if os.environ.get("AXES_ENABLED", "true").lower() == "true" else False
AXES_CACHE = "default"

RATELIMIT_CACHE = os.getenv('RATELIMIT_CACHE', 'default')
RATELIMIT_KEY = os.getenv('RATELIMIT_KEY', 'ip')
RATELIMIT_RATE = os.getenv('RATELIMIT_RATE', '150/m')
RATELIMIT_METHOD = os.getenv('RATELIMIT_METHOD', 'ALL')
RATELIMIT_GROUP = os.getenv('RATELIMIT_GROUP', 'graphql')
RATELIMIT_SKIP_TIMEOUT = os.getenv('RATELIMIT_SKIP_TIMEOUT', 'False')

# CSRF settings
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
# session cookie validity = 8 hours
SESSION_COOKIE_AGE = 28800
SESSION_COOKIE_NAME = "openimis_session"

# CORS settings
CORS_ALLOW_CREDENTIALS = True

# Cookie settings
CSRF_COOKIE_NAME = 'csrftoken'
CSRF_USE_SESSIONS = True
SESSION_COOKIE_SAMESITE = 'Lax'  # or 'None' if cross-site
CSRF_COOKIE_SAMESITE = 'Lax'  # or 'None' if cross-site
CSRF_COOKIE_HTTPONLY = False  # False if you need to access it from JavaScript

USER_AGENT_CSRF_BYPASS = [bypass.strip() for bypass in os.getenv("USER_AGENT_CSRF_BYPASS", '').split(',') if bypass != '']
# Adjust other settings as needed for your specific application
# ...

# If using GraphQL, ensure the CSRF_EXEMPT_LIST includes your GraphQL endpoint
# CSRF_EXEMPT_LIST = ['/graphql/']  # Adjust as needed

# There used to be a default password for zip files but for security reasons, it was removed. Trying to export
# without a password defined is going to fail
MASTER_DATA_PASSWORD = os.environ.get("MASTER_DATA_PASSWORD", None)

PASSWORD_MIN_LENGTH = int(os.getenv('PASSWORD_MIN_LENGTH', 8))
PASSWORD_UPPERCASE = int(os.getenv('PASSWORD_UPPERCASE', 1))
PASSWORD_LOWERCASE = int(os.getenv('PASSWORD_LOWERCASE', 1))
PASSWORD_DIGITS = int(os.getenv('PASSWORD_DIGITS', 1))
PASSWORD_SYMBOLS = int(os.getenv('PASSWORD_SYMBOLS', 1))

CSP_DEFAULT_SRC = ["'self'"]
CSP_SCRIPT_SRC = ["'self'"]
CSP_STYLE_SRC = ["'self'"]
CSP_IMG_SRC = ["'self'", "data:"]  # Allows images from the same origin and base64 encoded images
CSP_FRAME_ANCESTORS = ["'self'"]

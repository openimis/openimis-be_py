import os
GRAPHQL_JWT.update({
    "JWT_COOKIE_SECURE": True,
    "JWT_COOKIE_SAMESITE": "Lax",
})
# Fetch protocols and hosts from environment variables
protos = [proto.strip() for proto in os.environ.get('PROTOS', 'http,https').split(',') if proto.strip()]
hosts = [host.strip() for host in os.environ.get('HOSTS', '').split(',') if host.strip()]

# Set ALLOWED_HOSTS
ALLOWED_HOSTS = hosts if hosts else ['*']
print("ALLOWED_HOSTS:", ALLOWED_HOSTS)

# Create CSRF_TRUSTED_ORIGINS by combining protocols and hosts
CSRF_TRUSTED_ORIGINS = [f'{proto}://{host}' for proto in protos for host in hosts if host]
print("CSRF_TRUSTED_ORIGINS:", CSRF_TRUSTED_ORIGINS)
# If ALLOWED_HOSTS is ['*'], set a default for CSRF_TRUSTED_ORIGINS
if not CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS = []

# Set CORS_ALLOWED_ORIGINS to match CSRF_TRUSTED_ORIGINS
CORS_ALLOWED_ORIGINS = CSRF_TRUSTED_ORIGINS
print("CORS_ALLOWED_ORIGINS:", CORS_ALLOWED_ORIGINS)
# Determine if we're behind a proxy (using http in protos indicates proxy use)
BEHIND_PROXY = 'http' in protos

# Security settings
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = BEHIND_PROXY
SECURE_SSL_REDIRECT = not BEHIND_PROXY  # Only redirect if not behind a proxy

# HSTS settings (if using HTTPS)
if 'https' in protos:
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_HSTS_REDIRECT = True

# Additional security settings
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

ASYNC = os.environ.get('ASYNC', True)
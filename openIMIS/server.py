import socket
from waitress import serve

from openIMIS.wsgi import application

trusted_proxy = "*"  # Safe, because backend can only be proxied from frontend
trusted_proxy_headers = (
    "x-forwarded-host",
    "x-forwarded-for",
    "x-forwarded-proto",
    "x-forwarded-port",
    "x-forwarded-by"
)

serve_kwargs = {
    "listen": "0.0.0.0:8000",
}

if trusted_proxy:
    serve_kwargs["trusted_proxy"] = trusted_proxy
    serve_kwargs["trusted_proxy_headers"] = trusted_proxy_headers

if __name__ == '__main__':
    serve(application, **serve_kwargs)

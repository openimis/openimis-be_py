import os 

OPEN_SEARCH_HTTP_PORT = os.environ.get("OPEN_SEARCH_HTTP_PORT", "9200")
OPENSEARCH_DSL_AUTOSYNC = os.environ.get('OPENSEARCH_DSL_AUTOSYNC', 'True') == 'True' 

OPENSEARCH_DSL = {
    'default': {
        'hosts': [host.strip() for host in os.getenv("OPENSEARCH_HOSTS", 'opensearch:9200').split(',') if host != ''],
        'http_auth': (
            f"{os.environ.get('OPENSEARCH_ADMIN')}",
            f"{os.environ.get('OPENSEARCH_PASSWORD')}"
        ),
        'timeout': 120,
        # CA bundle for an https host signed by a private authority. Unset keeps
        # opensearch-py's default (SSL_CERT_FILE/SSL_CERT_DIR, then certifi);
        # ignored for http.
        'ca_certs': os.environ.get('OPENSEARCH_CA_CERTS') or None,
    }
}

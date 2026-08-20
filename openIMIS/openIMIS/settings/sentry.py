import os
import logging

logger = logging.getLogger(__name__)

try:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
except ModuleNotFoundError:
    sentry_sdk = None
    DjangoIntegration = None
    logger.error(
        "sentry_sdk has to be installed to use Sentry. Run `pip install --upgrade sentry_sdk` to install it."
    )

try:
    # scrubber is supportedb by version 1.29 or higher
    from sentry_sdk.scrubber import DEFAULT_DENYLIST, EventScrubber
    HAS_SCRUBBER = True
except ModuleNotFoundError:
    DEFAULT_DENYLIST = []
    EventScrubber = None
    HAS_SCRUBBER = False
    logger.error(
        "You need to upgrade sentry_sdk to Version >= 1.29. Run `pip install --upgrade sentry_sdk` to upgrade it."
    )

SENTRY_DSN = os.environ.get("SENTRY_DSN", None)
SENTRY_SAMPLE_RATE = os.environ.get("SENTRY_SAMPLE_RATE", "0.2")
IS_SENTRY_ENABLED = False

SENSITIVE_KEYS = {
    "password", "passwd", "pwd",
    "token", "access_token", "refresh_token",
    "authorization", "auth",
    "api_key", "apikey",
    "secret",
    "host", "port", "user", "username",
    "dbname"
}

denylist = DEFAULT_DENYLIST + ["dsn", "conn_params"]
denylist += list(SENSITIVE_KEYS)

def sanitize(value):
    """Nettoyage récursif"""
    if isinstance(value, dict):
        clean = {}
        for k, v in value.items():
            if any(s in k.lower() for s in SENSITIVE_KEYS):
                clean[k] = "***"
            else:
                clean[k] = sanitize(v)
        return clean

    elif isinstance(value, list):
        return [sanitize(v) for v in value]

    return value


def before_send(event, hint):
    try:
        # Nettoyage global (clé principale)
        event = sanitize(event)

        # Cas spécifique : exception message
        if "exception" in event:
            for exc in event["exception"].get("values", []):
                if "value" in exc:
                    exc["value"] = sanitize(exc["value"])

                # stacktrace
                if "stacktrace" in exc:
                    for frame in exc["stacktrace"].get("frames", []):
                        if "vars" in frame:
                            frame["vars"] = sanitize(frame["vars"])

        return event

    except Exception:
        # En cas de bug dans le scrubber, ne jamais bloquer Sentry
        return event

init_kwargs = {
    "dsn": SENTRY_DSN,
    "integrations": [DjangoIntegration()] if DjangoIntegration else [],
    "traces_sample_rate": float(SENTRY_SAMPLE_RATE),
    "send_default_pii": False,
    "before_send": before_send,
}

if HAS_SCRUBBER:
    init_kwargs["event_scrubber"] = EventScrubber(
        denylist=denylist
    )

if SENTRY_DSN is not None:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration

        sentry_sdk.init(**init_kwargs)
        IS_SENTRY_ENABLED = True
    except ModuleNotFoundError:
        logger.error(
            "sentry_sdk has to be installed to use Sentry. Run `pip install --upgrade sentry_sdk` to install it."
        )

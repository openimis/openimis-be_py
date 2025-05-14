import os

SENTRY_DSN = os.environ.get("SENTRY_DSN", None)
SENTRY_SAMPLE_RATE = os.environ.get("SENTRY_SAMPLE_RATE", "0.2")
IS_SENTRY_ENABLED = False

if SENTRY_DSN is not None:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration

        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[DjangoIntegration()],
            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            # We recommend adjusting this value in production,
            traces_sample_rate=float(SENTRY_SAMPLE_RATE),
            # If you wish to associate users to errors (assuming you are using
            # django.contrib.auth) you may enable sending PII data.
            send_default_pii=True,
            # By default the SDK will try to use the SENTRY_RELEASE
            # environment variable, or infer a git commit
            # SHA as release, however you may want to set
            # something more human-readable.
            # release="myapp@1.0.0",
        )
        IS_SENTRY_ENABLED = True
    except ModuleNotFoundError:
        logging.error(
            "sentry_sdk has to be installed to use Sentry. Run `pip install --upgrade sentry_sdk` to install it."
        )

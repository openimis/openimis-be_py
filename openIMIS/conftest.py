import pytest


@pytest.hookimpl(trylast=True)
def pytest_configure(config):
    """
    Disable password validation for pytest runs, after Django has finished
    configuring itself (hence trylast=True, so pytest-django's own
    pytest_configure - which calls django.setup() - has already run).

    The shared FHIR test fixtures (GenericFhirAPITestMixin.setUp(),
    create_test_interactive_user(), etc., used by virtually every test under
    api_fhir_r4.tests and beyond) create test users with a fixed, simple
    password ("admin123") for convenience. That password does not satisfy
    this project's configured password policy (min length/uppercase/
    lowercase/digit/symbol requirements plus a zxcvbn strength check - see
    openIMIS.settings.security and core.utils.CustomPasswordValidator).

    Under `manage.py test` this happens not to cause failures in practice
    (Django's cached default password validators end up built against a
    lenient state depending on process bootstrap/import order), but
    pytest-django applies the configured policy consistently, so user
    creation fails validation. We can't fix this with a plain module-level
    env var override (os.environ.setdefault) in this file: this project's
    settings module (openIMIS.settings) reads python-dotenv values as part
    of `django.setup()`, which pytest-django triggers before this file's
    top-level code runs. So instead we mutate the already-loaded settings
    directly, once Django is configured, and clear the validator cache.
    """
    from django.conf import settings

    if not settings.configured:
        return

    settings.AUTH_PASSWORD_VALIDATORS = []
    from django.contrib.auth.password_validation import get_default_password_validators

    get_default_password_validators.cache_clear()

from .common import BASE_DIR
# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = "en-GB"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = False

# List of places to look for translations, this could include an external translation module
LOCALE_PATHS = get_locale_folders() + [
    os.path.join(BASE_DIR, "locale"),
]

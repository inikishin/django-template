from app.config.environ import BASE_DIR

LANGUAGE_CODE = "ru"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Languages available for translation.
LANGUAGES = [
    ("ru", "Russian"),
    ("en", "English"),
]
# Directory with .po/.mo translation catalogs (manage.py makemessages/compilemessages).
LOCALE_PATHS = [BASE_DIR / "locale"]

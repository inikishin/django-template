# Settings are split into separate modules in the `app.config` package
# using django-split-settings. Only the most basic ones are kept here.
from split_settings.tools import include

from app.config.environ import env

# SECURITY WARNING: keep the secret key secret in production.
SECRET_KEY = env("SECRET_KEY", default="insecure-change-me")

# SECURITY WARNING: don't run production with DEBUG turned on.
DEBUG = env.bool("DEBUG", default=False)

include(
    "config/installed_apps.py",
    "config/middleware.py",
    "config/api.py",
    "config/auth.py",
    "config/db.py",
    "config/http.py",
    "config/i18n.py",
    "config/templates.py",
    "config/static.py",
    "config/media.py",
    "config/logging.py",
)

ROOT_URLCONF = "app.urls"
WSGI_APPLICATION = "app.wsgi.application"
ASGI_APPLICATION = "app.asgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

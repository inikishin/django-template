from app.config.environ import env

# Core Django apps.
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

# Third-party apps.
THIRD_PARTY_APPS = [
    "rest_framework",
    "django_filters",
    "corsheaders",
    "drf_spectacular",
    "drf_spectacular_sidecar",
]

# Project apps. Add each new microservice app here.
LOCAL_APPS = [
    "app",
    "users",
    "posts",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Apps available only when DEBUG is enabled.
if env.bool("DEBUG", default=False):
    INSTALLED_APPS += []

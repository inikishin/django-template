import os
from pathlib import Path

from dotenv import load_dotenv
from split_settings.tools import include

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
DEBUG = True if os.getenv("DEBUG") else False

include(
    "components/apps.py",
    "components/auth.py",
    "components/apps.py",
    "components/db.py",
    "components/drf.py",
    "components/http.py",
    "components/localization.py",
    "components/middleware.py",
    "components/swagger.py",
    "components/templates.py",
)

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
STATIC_URL = "static/"

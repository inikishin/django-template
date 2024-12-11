import os


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.getenv("DB_HOST"),
        "PORT": int(os.getenv("DB_PORT", 0)),
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASS"),
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

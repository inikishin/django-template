from app.config.environ import env

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": env("DB_HOST", default="localhost"),
        "PORT": env.int("DB_PORT", default=5432),
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASS"),
    }
}

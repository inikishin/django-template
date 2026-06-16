from app.config.environ import env

REDIS_URL = env("REDIS_URL", default="redis://localhost:6379/0")

# In tests, use a local in-memory cache to avoid depending on Redis.
if env.bool("USE_IN_MEMORY_CACHE", default=False):
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
        }
    }

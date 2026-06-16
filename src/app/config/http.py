from app.config.environ import env

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

CORS_ALLOW_ALL_ORIGINS = env.bool("CORS_ALLOW_ALL_ORIGINS", default=True)
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# Location prefix for all API routes (e.g. "api" -> /api/...). Configurable so the
# service can be mounted under any path behind a gateway. Empty -> routes at root.
API_PREFIX = env("API_PREFIX", default="api").strip("/")

REST_FRAMEWORK = {
    # No authentication by default; enable an auth bundle via the initial-setup skill.
    "DEFAULT_AUTHENTICATION_CLASSES": (),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.AllowAny",),
    "DEFAULT_PAGINATION_CLASS": "app.api.pagination.StandardResultsSetPagination",
    "PAGE_SIZE": 100,
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Django microservice API",
    "DESCRIPTION": "API backend микросервиса",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    # The sidecar serves swagger-ui/redoc static files locally, without a CDN.
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
}

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "config.pagination.StandardResultsSetPagination",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}

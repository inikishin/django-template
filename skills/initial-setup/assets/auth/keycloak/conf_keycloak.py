from app.config.environ import env

# Settings for drf-keycloak-auth (as in the reference project).
KEYCLOAK_CONFIG = {
    "KEYCLOAK_SERVER_URL": env("KEYCLOAK_SERVER_URL"),
    "KEYCLOAK_REALM": env("KEYCLOAK_REALM", default="master"),
    "KEYCLOAK_CLIENT_ID": env("KEYCLOAK_CLIENT_ID"),
    "KEYCLOAK_CLIENT_SECRET_KEY": env("KEYCLOAK_CLIENT_SECRET_KEY"),
    # Keycloak roles that map to Django is_staff.
    "KEYCLOAK_ROLES_TO_DJANGO_IS_STAFF": ["admin"],
}

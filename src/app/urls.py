from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

# API location prefix is configurable via the API_PREFIX setting / env var.
api = f"{settings.API_PREFIX}/" if settings.API_PREFIX else ""

# Application API routes. Add a new app's urlconf here.
api_urlpatterns = [
    path("posts/", include("posts.urls")),
    path("users/", include("users.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    # OpenAPI schema and documentation UI.
    path(f"{api}schema/", SpectacularAPIView.as_view(), name="schema"),
    path(f"{api}swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path(f"{api}redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path(api, include(api_urlpatterns)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

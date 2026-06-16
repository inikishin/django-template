from django.urls import include, path

from app.api.routers import DefaultRouter
from users.api.viewsets import UserViewSet

router = DefaultRouter()
router.register("", UserViewSet, basename="users")

urlpatterns = [
    path("", include(router.urls)),
]

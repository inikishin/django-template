from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import UsersViewSet

router = DefaultRouter()
router.register(r"", UsersViewSet, basename="users")

urlpatterns = [
    path("", include(router.urls)),
]

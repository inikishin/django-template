from django.urls import include, path

from app.api.routers import DefaultRouter
from posts.api.viewsets import PostViewSet

router = DefaultRouter()
router.register("", PostViewSet, basename="posts")

urlpatterns = [
    path("", include(router.urls)),
]

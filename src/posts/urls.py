from django.urls import include, path
from rest_framework.routers import DefaultRouter

from posts.api.v1 import views

router = DefaultRouter()
router.register("", views.PostViewSet, basename="posts")

urlpatterns = [
    path("", include(router.urls)),
]

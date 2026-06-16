from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from app.api.viewsets import DefaultModelViewSet
from posts.api.filtersets import PostFilterSet
from posts.api.schema import PostViewSetSchema
from posts.api.serializers import (
    PostDetailSerializer,
    PostListSerializer,
    PostWriteSerializer,
)
from posts.models import Post
from posts.services.post import SimilarPostsService


@extend_schema_view(**PostViewSetSchema)
class PostViewSet(DefaultModelViewSet):
    queryset = Post.objects.all().order_by("-updated_at")
    serializer_class = PostDetailSerializer
    filterset_class = PostFilterSet
    serializer_action_classes = {
        "list": PostListSerializer,
        "retrieve": PostDetailSerializer,
        "create": PostWriteSerializer,
        "update": PostWriteSerializer,
        "partial_update": PostWriteSerializer,
        "similar": PostListSerializer,
    }

    def get_queryset(self):
        if self.action == "list":
            return Post.objects.published().order_by("-updated_at")
        return super().get_queryset()

    @extend_schema(summary="Похожие статьи", responses=PostListSerializer(many=True))
    @action(detail=True, methods=["get"])
    def similar(self, request: Request, *args, **kwargs) -> Response:
        """Posts with overlapping tags (business logic lives in the service)."""
        queryset = SimilarPostsService(self.get_object())()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

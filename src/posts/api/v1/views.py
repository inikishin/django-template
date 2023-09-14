from uuid import UUID

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from posts.api.v1.filtersets import PostFilterSet
from posts.api.v1.serializers import (
    PostListSerializer,
    PostRetrieveSerializer,
    PostSerializer,
    TagListSerializer,
)
from posts.models import Post, Tag

TAGS = ["posts"]


class PostViewSet(ReadOnlyModelViewSet):
    queryset = Post.objects.filter(is_draft=False).order_by("-modified_at")
    serializer_class = PostSerializer
    filterset_class = PostFilterSet
    filter_backends = [DjangoFilterBackend]

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        if self.action == "retrieve":
            return PostRetrieveSerializer
        if self.action == "get_tags":
            return TagListSerializer
        return PostListSerializer

    @swagger_auto_schema(
        tags=TAGS,
        operation_summary="Get list of posts",
        operation_description="Get list of posts. Available to sort and filter posts.",
    )
    def list(self, request: Request, *args, **kwargs) -> Response:
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=TAGS,
        operation_summary="Get post",
        operation_description="Get post data.",
    )
    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        return super().retrieve(request, *args, **kwargs)

    @action(
        methods=["GET"],
        detail=False,
        url_path="tags",
        queryset=Tag.objects.filter(is_active=True).order_by("id"),
        serializer_class=TagListSerializer,
        filterset_class=None,
    )
    @swagger_auto_schema(
        tags=TAGS,
        operation_summary="Get list of tags",
        operation_description="Get list of tags.",
    )
    def get_tags(self, request: Request) -> Response:
        return super().list(request)

    @action(
        methods=["GET"],
        detail=True,
        url_path="similar-posts",
    )
    @swagger_auto_schema(
        tags=TAGS,
        operation_summary="Get similar posts",
        operation_description="Get list of similar posts posts.",
    )
    def get_similar_posts(self, request: Request, pk: UUID) -> Response:
        post = get_object_or_404(Post, id=pk)
        tags = post.tags.all()
        self.queryset = (
            Post.objects.filter(tags__in=tags).exclude(id=pk).order_by("-modified_at")
        )
        return super().list(request)

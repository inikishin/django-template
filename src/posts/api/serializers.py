from rest_framework import serializers

from app.api.serializers import ReadOnlyModelSerializer
from posts.models import Post, Tag
from users.api.serializers import UserListSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "is_active"]


class PostListSerializer(ReadOnlyModelSerializer):
    """Serializer for the list of posts (read-only)."""

    author = UserListSerializer()
    tags = TagSerializer(many=True)

    class Meta:
        model = Post
        fields = ["id", "title", "description", "slug", "author", "language", "tags"]


class PostDetailSerializer(ReadOnlyModelSerializer):
    """Full post serializer for retrieve and create/update responses."""

    author = UserListSerializer()
    tags = TagSerializer(many=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "description",
            "slug",
            "content",
            "author",
            "language",
            "is_draft",
            "tags",
            "created_at",
            "updated_at",
        ]


class PostWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating a post."""

    class Meta:
        model = Post
        fields = ["title", "description", "content", "author", "language", "is_draft", "tags"]

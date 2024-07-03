from rest_framework import serializers

from posts.models import Post, Tag
from users.serializers import UserListSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class TagListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["name"]


class TagRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class PostSerializer(serializers.ModelSerializer):
    author = UserListSerializer()

    class Meta:
        model = Post
        fields = "__all__"


class PostListSerializer(serializers.ModelSerializer):
    author = UserListSerializer()
    tags = TagListSerializer(many=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "description",
            "image_url",
            "slug",
            "author",
            "language",
            "tags",
        ]


class PostRetrieveSerializer(serializers.ModelSerializer):
    author = UserListSerializer()

    class Meta:
        model = Post
        fields = "__all__"

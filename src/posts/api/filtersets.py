from django_filters import rest_framework as filters

from app.api.filtersets import SearchFilterSet
from posts.constants import POST_SEARCH_FIELDS
from posts.models import Post, Tag


class PostFilterSet(SearchFilterSet):
    search_fields = POST_SEARCH_FIELDS

    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__name",
        to_field_name="name",
        queryset=Tag.objects.all(),
    )
    author = filters.CharFilter(field_name="author__username")

    ordering = filters.OrderingFilter(
        fields={
            "title": "title",
            "created_at": "created_at",
            "updated_at": "updated_at",
        },
    )

    class Meta:
        model = Post
        fields = ["slug", "author", "language", "is_draft", "tags"]


class TagFilterSet(SearchFilterSet):
    search_fields = ["name"]

    class Meta:
        model = Tag
        fields = ["is_active"]

from django_filters import rest_framework as filters

from posts.models import Post, Tag


class PostFilterSet(filters.FilterSet):
    author = filters.CharFilter(field_name="author__username")
    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__name",
        to_field_name="name",
        queryset=Tag.objects.all(),
    )

    search_fields = [
        "title",
        "description",
        "header",
    ]

    ordering = [
        "title",
        "author",
        "modified_at",
    ]

    class Meta:
        model = Post
        fields = [
            "slug",
            "author",
            "language",
            "tags",
        ]

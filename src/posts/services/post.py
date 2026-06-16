from django.db.models import QuerySet

from posts.models import Post


class SimilarPostsService:
    """Published posts sharing tags with the given one, most recent first."""

    def __init__(self, post: Post) -> None:
        self.post = post

    def __call__(self) -> QuerySet[Post]:
        return (
            Post.objects.published()
            .filter(tags__in=self.post.tags.all())
            .exclude(pk=self.post.pk)
            .distinct()
            .order_by("-updated_at")
        )

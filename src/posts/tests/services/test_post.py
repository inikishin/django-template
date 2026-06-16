import pytest
from django_dynamic_fixture import G

from posts.models import Post, Tag
from posts.services.post import SimilarPostsService


@pytest.mark.django_db
class TestSimilarPostsService:
    def test_returns_published_posts_with_shared_tags(self):
        tag = G(Tag)
        post = G(Post, is_draft=False, tags=[tag])
        similar = G(Post, is_draft=False, tags=[tag])
        G(Post, is_draft=False)  # no shared tags -> excluded

        result = SimilarPostsService(post)()

        assert set(result) == {similar}

    def test_excludes_drafts(self):
        tag = G(Tag)
        post = G(Post, is_draft=False, tags=[tag])
        G(Post, is_draft=True, tags=[tag])  # draft -> excluded

        assert list(SimilarPostsService(post)()) == []

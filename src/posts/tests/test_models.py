import pytest
from django_dynamic_fixture import G

from posts.models import Post


@pytest.mark.django_db
class TestPostQuerySet:
    def test_published_excludes_drafts(self):
        G(Post, is_draft=False)
        G(Post, is_draft=True)

        assert Post.objects.published().count() == 1

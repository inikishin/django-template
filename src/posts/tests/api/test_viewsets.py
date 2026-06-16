import pytest
from django_dynamic_fixture import G

from posts.models import Post, Tag


@pytest.mark.django_db
class TestPostViewSet:
    def test_list_returns_only_published(self, as_user):
        G(Post, is_draft=False)
        G(Post, is_draft=True)

        result = as_user.get("/api/posts/")

        assert result["count"] == 1

    def test_retrieve(self, as_user):
        post = G(Post, is_draft=False)

        result = as_user.get(f"/api/posts/{post.pk}/")

        assert result["id"] == str(post.pk)
        assert result["title"] == post.title

    def test_create(self, as_user, user):
        data = {
            "title": "Test article",
            "content": "Article body",
            "author": user.pk,
            "language": "ru",
            "is_draft": False,
        }

        result = as_user.post("/api/posts/", data)

        assert Post.objects.count() == 1
        # slug is filled automatically from the title (calculate_slug).
        assert result["slug"]

    def test_partial_update(self, as_user):
        post = G(Post, is_draft=True)

        result = as_user.patch(f"/api/posts/{post.pk}/", {"is_draft": False})

        assert result["is_draft"] is False

    def test_bulk_delete(self, as_user):
        posts = G(Post, n=3)

        as_user.delete("/api/posts/", {"ids": [p.pk for p in posts]})

        assert Post.objects.count() == 0

    def test_search(self, as_user):
        G(Post, title="django microservice", is_draft=False)
        G(Post, title="something else", is_draft=False)

        result = as_user.get("/api/posts/?search=django")

        assert result["count"] == 1

    def test_similar_posts(self, as_user):
        tag = G(Tag)
        post = G(Post, is_draft=False, tags=[tag])
        similar = G(Post, is_draft=False, tags=[tag])
        G(Post, is_draft=False)  # no shared tags

        result = as_user.get(f"/api/posts/{post.pk}/similar/")

        assert {item["id"] for item in result["results"]} == {str(similar.pk)}

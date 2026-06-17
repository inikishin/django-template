---
name: generate-api-method
description: >-
  Creating a new API method/endpoint in this Django + DRF microservice following
  project conventions: viewset on base classes, per-action serializers
  (serializer_action_classes), filtering via SearchFilterSet, swagger descriptions
  via extend_schema, registration in the router, custom
  @action. Use when adding a CRUD endpoint, a new ViewSet, or a custom action.
  Keywords: endpoint, API method, viewset, serializer, @action, route, swagger,
  filter.
metadata:
  type: project-convention
  language: en
---

# Creating an API method

Check against the structure (skill `project-structure`). Endpoint files live in
`<app>/api/`. The model must exist (skill `create-model`).

The JSON format is the DRF standard (field names in `snake_case`).

## 1. Serializers — `<app>/api/serializers.py`

Create separate serializers per action:

- list (`list`) — lightweight, read-only (`ReadOnlyModelSerializer`);
- detail (`retrieve`) — full, read-only;
- write (`create`/`update`) — fields available for input.

```python
from rest_framework import serializers
from app.api.serializers import ReadOnlyModelSerializer
from posts.models import Post
from users.api.serializers import UserListSerializer


class PostListSerializer(ReadOnlyModelSerializer):
    author = UserListSerializer()

    class Meta:
        model = Post
        fields = ["id", "title", "slug", "author", "language"]


class PostWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["title", "content", "author", "language", "is_draft", "tags"]
```

## 2. FilterSet — `<app>/api/filtersets.py`

Inherit from `SearchFilterSet`, set `search_fields` (the `?search=` parameter).
Add filters and an `OrderingFilter` (specify the sort keys explicitly).

```python
from django_filters import rest_framework as filters
from app.api.filtersets import SearchFilterSet
from posts.models import Post


class PostFilterSet(SearchFilterSet):
    search_fields = ["title", "description", "content"]
    author = filters.CharFilter(field_name="author__username")
    ordering = filters.OrderingFilter(fields={"created_at": "created_at", "title": "title"})

    class Meta:
        model = Post
        fields = ["slug", "language", "is_draft"]
```

## 3. Schema for swagger — `<app>/api/schema.py`

For EVERY public method set `summary` and `description` (otherwise the schema will
end up with an uninformative default description). Assemble a dict for
`extend_schema_view`.

```python
from drf_spectacular.utils import extend_schema
from posts.api.serializers import PostDetailSerializer, PostListSerializer

TAGS = ["posts"]

PostViewSetSchema = {
    "list": extend_schema(tags=TAGS, summary="Список статей", responses=PostListSerializer),
    "retrieve": extend_schema(tags=TAGS, summary="Получить статью", responses=PostDetailSerializer),
    "create": extend_schema(tags=TAGS, summary="Создать статью", responses=PostDetailSerializer),
}
```

## 4. Service (business logic) — `<app>/services/`

Implement business logic as **class-based services — always classes, even with a
single method**. The convention: accept input data in `__init__`, invoke the single
operation via `__call__` (for multiple operations, use named methods). Services are
called by views, admin actions, CLI commands, and Celery tasks.

```python
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
```

## 5. ViewSet — `<app>/api/viewsets.py`

Base classes:

- `DefaultModelViewSet` — full CRUD. On `create`/`update` the response is returned by
  the retrieve serializer (validate with one, respond with another).
- `ReadonlyModelViewSet` — only `list` + `retrieve`.

Per-action serializers go through `serializer_action_classes`. Keep the viewset
**thin**: only request/validation/response. Call business logic from `<app>/services/`,
and reusable queries from the queryset/manager (repository pattern); don't proliferate
`filter()` in the viewset.

```python
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.response import Response

from app.api.viewsets import DefaultModelViewSet
from posts.api.filtersets import PostFilterSet
from posts.api.schema import PostViewSetSchema
from posts.api.serializers import PostDetailSerializer, PostListSerializer, PostWriteSerializer
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
            return Post.objects.published().order_by("-updated_at")  # query - in queryset
        return super().get_queryset()

    @extend_schema(summary="Похожие статьи", responses=PostListSerializer(many=True))
    @action(detail=True, methods=["get"])
    def similar(self, request, *args, **kwargs) -> Response:
        """Posts with overlapping tags."""
        queryset = SimilarPostsService(self.get_object())()  # logic - in service
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
```

**URL naming for `@action`.** The Python method is `snake_case` (PEP8), but in the URL
we use **kebab-case** for compound names — set it explicitly via `url_path` (and
`url_name` if needed):

```python
@action(detail=True, methods=["get"], url_path="similar-posts")
def similar_posts(self, request, *args, **kwargs) -> Response:
    ...
# -> GET /api/posts/{id}/similar-posts/
```

Without `url_path` DRF takes the method name as is (`similar_posts`) — so for
compound names always specify `url_path` in kebab-case.

## 6. Routing — `<app>/urls.py`

Register the viewset in `DefaultRouter` (DELETE on the list url = bulk delete
`bulk_delete` by `{"ids": [...]}`). Then mount the app in `app/urls.py`.

```python
from django.urls import include, path
from app.api.routers import DefaultRouter
from posts.api.viewsets import PostViewSet

router = DefaultRouter()
router.register("", PostViewSet, basename="posts")
urlpatterns = [path("", include(router.urls))]
```

The resulting method path is `/<API_PREFIX>/<app>/...` (by default `/api/posts/...`).
The prefix is set by the `API_PREFIX` environment variable (no `v1` version).

## Permissions

By default access is open (`AllowAny` in `app/config/api.py`) — the base template has no
authentication. If authentication is enabled (jwt/oauth, see skill `initial-setup`),
`IsAuthenticated` applies globally. Override `permission_classes` on the viewset when
needed (`app.api.permissions.ReadOnly` and others).

## Checklist

- [ ] list/detail/write serializers.
- [ ] `serializer_action_classes` mapped to actions.
- [ ] FilterSet based on `SearchFilterSet`, `search_fields` set.
- [ ] `summary`/`description` in the schema for all public methods.
- [ ] Viewset on `DefaultModelViewSet`/`ReadonlyModelViewSet`, thin.
- [ ] Business logic — in `<app>/services/` (class-based service, even with a single method);
      queries — in the queryset/manager (not in the viewset).
- [ ] Registered in the router and mounted in `app/urls.py`.
- [ ] Custom `@action`s with compound names have `url_path` in kebab-case.
- [ ] Endpoint tests (skill `backend-testing`).
- [ ] `make lint` passes.

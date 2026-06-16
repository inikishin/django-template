---
name: generate-api-method
description: >-
  Создание нового метода/эндпоинта API в этом микросервисе на Django + DRF по
  конвенциям проекта: viewset на базовых классах, сериализаторы под действия
  (serializer_action_classes), фильтрация через SearchFilterSet, описание для swagger
  через extend_schema, регистрация в роутере, кастомные
  @action. Используй при добавлении CRUD-эндпоинта, нового ViewSet или кастомного
  действия. Ключевые слова: эндпоинт, метод API, viewset, сериализатор, @action,
  роут, swagger, фильтр, endpoint.
metadata:
  type: project-convention
  language: ru
---

# Создание метода API

Сверься со структурой (скил `project-structure`). Файлы эндпоинта живут в
`<app>/api/`. Модель должна существовать (скил `create-model`).

Формат JSON — стандартный для DRF (имена полей в `snake_case`).

## 1. Сериализаторы — `<app>/api/serializers.py`

Заводим отдельные сериализаторы под действия:

- список (`list`) — лёгкий, только чтение (`ReadOnlyModelSerializer`);
- деталь (`retrieve`) — полный, только чтение;
- запись (`create`/`update`) — поля, доступные на ввод.

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

Наследуем `SearchFilterSet`, задаём `search_fields` (параметр `?search=`).
Добавляем фильтры и `OrderingFilter` (ключи сортировки задаём явно).

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

## 3. Схема для swagger — `<app>/api/schema.py`

Для КАЖДОГО публичного метода задаём `summary` и `description` (иначе в схеме
окажется неинформативное описание по умолчанию). Собираем словарь под
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

## 4. Сервис (бизнес-логика) — `<app>/services/`

Бизнес-логику оформляем как **class-based сервисы — всегда классы, даже с одним
методом**. Соглашение: входные данные принимаем в `__init__`, единственную операцию
вызываем через `__call__` (для нескольких операций — именованные методы). Сервис
вызывают вьюхи, экшены админки, CLI-команды, Celery-задачи.

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

Базовые классы:

- `DefaultModelViewSet` — полный CRUD. На `create`/`update` ответ отдаётся
  retrieve-сериализатором (валидируем одним, отвечаем другим).
- `ReadonlyModelViewSet` — только `list` + `retrieve`.

Сериализатор под действие — через `serializer_action_classes`. Вьюсет держим
**тонким**: только запрос/валидация/ответ. Бизнес-логику зовём из `<app>/services/`,
а переиспользуемые выборки — из queryset/manager (паттерн репозитория), не плодим
`filter()` во вьюсете.

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
            return Post.objects.published().order_by("-updated_at")  # выборка - в queryset
        return super().get_queryset()

    @extend_schema(summary="Похожие статьи", responses=PostListSerializer(many=True))
    @action(detail=True, methods=["get"])
    def similar(self, request, *args, **kwargs) -> Response:
        """Posts with overlapping tags."""
        queryset = SimilarPostsService(self.get_object())()  # логика - в сервисе
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
```

**Именование URL у `@action`.** Метод в Python — `snake_case` (PEP8), а в URL для
составных имён используем **kebab-case** — задаём явно через `url_path` (и при
необходимости `url_name`):

```python
@action(detail=True, methods=["get"], url_path="similar-posts")
def similar_posts(self, request, *args, **kwargs) -> Response:
    ...
# -> GET /api/posts/{id}/similar-posts/
```

Без `url_path` DRF возьмёт имя метода как есть (`similar_posts`) — поэтому для
составных имён `url_path` в kebab-case указываем всегда.

## 6. Роутинг — `<app>/urls.py`

Регистрируем вьюсет в `DefaultRouter` (DELETE на списковый url = массовое удаление
`bulk_delete` по `{"ids": [...]}`). Затем приложение подключаем в `app/urls.py`.

```python
from django.urls import include, path
from app.api.routers import DefaultRouter
from posts.api.viewsets import PostViewSet

router = DefaultRouter()
router.register("", PostViewSet, basename="posts")
urlpatterns = [path("", include(router.urls))]
```

Итоговый путь метода — `/<API_PREFIX>/<app>/...` (по умолчанию `/api/posts/...`).
Префикс задаётся переменной окружения `API_PREFIX` (без версии `v1`).

## Права доступа

По умолчанию доступ открыт (`AllowAny` в `app/config/api.py`) — в базовом шаблоне нет
авторизации. Если подключена авторизация (jwt/oauth, см. скил `initial-setup`),
глобально действует `IsAuthenticated`. `permission_classes` на вьюсете переопределяем
при необходимости (`app.api.permissions.ReadOnly` и др.).

## Чек-лист

- [ ] Сериализаторы list/detail/write.
- [ ] `serializer_action_classes` сопоставлены действиям.
- [ ] FilterSet на базе `SearchFilterSet`, `search_fields` заданы.
- [ ] `summary`/`description` в схеме для всех публичных методов.
- [ ] Вьюсет на `DefaultModelViewSet`/`ReadonlyModelViewSet`, тонкий.
- [ ] Бизнес-логика — в `<app>/services/` (class-based сервис, даже с одним методом);
      выборки — в queryset/manager (не во вьюсете).
- [ ] Зарегистрирован в роутере и подключён в `app/urls.py`.
- [ ] У кастомных `@action` с составным именем — `url_path` в kebab-case.
- [ ] Тесты эндпоинта (скил `backend-testing`).
- [ ] `make lint` проходит.

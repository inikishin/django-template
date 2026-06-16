from drf_spectacular.utils import extend_schema

from posts.api.serializers import PostDetailSerializer, PostListSerializer

TAGS = ["posts"]

PostViewSetSchema = {
    "list": extend_schema(
        tags=TAGS,
        summary="Список статей",
        description="Возвращает список опубликованных статей. Доступны поиск, фильтрация и сортировка.",
        responses=PostListSerializer,
    ),
    "retrieve": extend_schema(
        tags=TAGS,
        summary="Получить статью",
        responses=PostDetailSerializer,
    ),
    "create": extend_schema(
        tags=TAGS,
        summary="Создать статью",
        responses=PostDetailSerializer,
    ),
    "update": extend_schema(
        tags=TAGS,
        summary="Обновить статью",
        responses=PostDetailSerializer,
    ),
    "partial_update": extend_schema(
        tags=TAGS,
        summary="Частично обновить статью",
        responses=PostDetailSerializer,
    ),
    "destroy": extend_schema(tags=TAGS, summary="Удалить статью"),
}

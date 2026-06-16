from drf_spectacular.utils import extend_schema

from users.api.serializers import UserDetailSerializer, UserListSerializer

TAGS = ["users"]

UserViewSetSchema = {
    "list": extend_schema(tags=TAGS, summary="Список пользователей", responses=UserListSerializer),
    "retrieve": extend_schema(tags=TAGS, summary="Получить пользователя", responses=UserDetailSerializer),
}

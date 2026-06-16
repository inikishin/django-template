from drf_spectacular.utils import extend_schema_view

from app.api.viewsets import ReadonlyModelViewSet
from users.api.filtersets import UserFilterSet
from users.api.schema import UserViewSetSchema
from users.api.serializers import UserDetailSerializer, UserListSerializer
from users.models import User


@extend_schema_view(**UserViewSetSchema)
class UserViewSet(ReadonlyModelViewSet):
    queryset = User.objects.all().order_by("id")
    serializer_class = UserDetailSerializer
    filterset_class = UserFilterSet
    serializer_action_classes = {
        "list": UserListSerializer,
        "retrieve": UserDetailSerializer,
    }

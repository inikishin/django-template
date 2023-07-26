from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from users.models import User
from users.serializers import UserSerializer


class UsersViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = None
    model = User
    serializer_class = UserSerializer
    queryset = model.objects.all()

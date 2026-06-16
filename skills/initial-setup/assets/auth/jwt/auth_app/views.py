from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from auth.serializers import LoginResponseSerializer, RefreshResponseSerializer

TAGS = ["auth"]


@extend_schema(tags=TAGS, summary="Вход (получение пары токенов)", responses=LoginResponseSerializer)
class LoginView(TokenObtainPairView):
    pass


@extend_schema(tags=TAGS, summary="Обновление access-токена", responses=RefreshResponseSerializer)
class RefreshView(TokenRefreshView):
    pass

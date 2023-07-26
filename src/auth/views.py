from drf_yasg.openapi import Schema
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from auth.serializers import (
    LoginResponseSerializer,
    RefreshResponseSerializer,
)

TAGS = ['auth']


class LoginView(TokenObtainPairView):
    @swagger_auto_schema(
        tags=TAGS,
        responses={
            status.HTTP_200_OK: LoginResponseSerializer,
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class RefreshView(TokenRefreshView):
    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: RefreshResponseSerializer,
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

#todo add black list method
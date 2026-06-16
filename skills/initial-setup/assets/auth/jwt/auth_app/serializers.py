from rest_framework import serializers


class LoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


class RefreshResponseSerializer(serializers.Serializer):
    access = serializers.CharField()

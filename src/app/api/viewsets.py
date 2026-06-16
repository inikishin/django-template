from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet


class ResponseWithRetrieveSerializerMixin:
    """
    Allows validating a request with one serializer and responding with another.

    The write serializer is set via `serializer_action_classes`, while the
    `retrieve` serializer (or `serializer_class`) is used for the response.

        class MyViewSet(DefaultModelViewSet):
            serializer_class = MyDetailSerializer
            serializer_action_classes = {
                "list": MyListSerializer,
                "create": MyWriteSerializer,
                "update": MyWriteSerializer,
                "partial_update": MyWriteSerializer,
            }
    """

    serializer_action_classes: dict = {}

    def get_serializer_class(self, action=None):
        if action is None:
            action = self.action
        try:
            return self.serializer_action_classes[action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()

    def response(self, instance, status_code, headers=None):
        """Serialize the instance with the retrieve serializer and return a Response."""
        retrieve_serializer_class = self.get_serializer_class(action="retrieve")
        serializer = retrieve_serializer_class(instance, context=self.get_serializer_context())
        return Response(serializer.data, status=status_code, headers=headers)


class DefaultCreateModelMixin(mixins.CreateModelMixin):
    """create() that responds with the retrieve serializer of the created object."""

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return self.response(instance, status.HTTP_201_CREATED, headers)

    def perform_create(self, serializer):
        return serializer.save()


class DefaultUpdateModelMixin(mixins.UpdateModelMixin):
    """update()/partial_update() that responds with the retrieve serializer of the object."""

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_update(serializer)
        return self.response(instance, status.HTTP_200_OK)

    def perform_update(self, serializer):
        return serializer.save()


class DefaultDestroyModelMixin(mixins.DestroyModelMixin):
    """Adds bulk deletion by a list of ids (DELETE on the list url)."""

    @extend_schema(summary="Массовое удаление", request=None, responses=None)
    def bulk_delete(self, request, *args, **kwargs) -> Response:
        """
        Delete objects by a list of ids.

        Example request body: {"ids": [1, 2, 3]}
        """
        if not isinstance(request.data, dict) or not request.data.get("ids"):
            raise ValidationError('Передайте список id для удаления: {"ids": [1, 2, 3]}')

        ids = request.data["ids"]
        for _id in ids:
            get_object_or_404(self.get_queryset(), pk=_id)

        self.get_queryset().filter(pk__in=ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DefaultModelViewSet(
    DefaultCreateModelMixin,
    mixins.RetrieveModelMixin,
    DefaultUpdateModelMixin,
    mixins.ListModelMixin,
    DefaultDestroyModelMixin,
    ResponseWithRetrieveSerializerMixin,
    GenericViewSet,
):
    """Full project CRUD viewset with support for serializer_action_classes."""


class ReadonlyModelViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    ResponseWithRetrieveSerializerMixin,
    GenericViewSet,
):
    """Read-only viewset (list + retrieve)."""

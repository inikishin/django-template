import uuid

from django.db import models


class UUIDIdMixin(models.Model):
    """Миксина для изменения первичного ключа на UUIDField."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimeStampedMixin(models.Model):
    """Миксина добавления авто полей created_at и modified_at."""

    created_at = models.DateTimeField(
        verbose_name="Дата создания записи", auto_now_add=True
    )
    modified_at = models.DateTimeField(
        verbose_name="Дата изменения записи", auto_now=True
    )

    class Meta:
        abstract = True


class IsActiveMixin(models.Model):
    """Миксина добавления признака is_active."""

    is_active = models.BooleanField(verbose_name="Активен", default=True)

    class Meta:
        abstract = True

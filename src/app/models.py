import uuid
from typing import Any

from django.db import models
from django.utils.translation import gettext_lazy as _

__all__ = [
    "models",
    "DefaultModel",
    "UUIDModel",
    "TimeStampedMixin",
    "IsActiveMixin",
    "MoneyField",
]


class DefaultModel(models.Model):
    """
    Base project model.

    - __str__ takes the `name` field by default.
    - If services need to run on save(), override `run_services`.
    - For computed fields, add a DB field and a `calculate_<field>` method;
      it will be called automatically before saving.
    - `update_from_kwargs` - update the instance from a dict.
    - `setattr_and_save` - convenient shortcut for tests.
    """

    class Meta:
        abstract = True

    def __str__(self) -> str:
        name = getattr(self, "name", None)
        if name is not None:
            return str(name)
        return super().__str__()

    def update_from_kwargs(self, **kwargs: Any) -> None:
        """Update the instance fields with values from kwargs."""
        for key, value in kwargs.items():
            setattr(self, key, value)

    def setattr_and_save(self, key: str, value: Any) -> None:
        """Set an attribute and save the instance (convenient in tests)."""
        setattr(self, key, value)
        self.save()

    def get_field_calculators(self) -> list:
        return [getattr(self, attr) for attr in dir(self) if attr.startswith("calculate_")]

    def update_calculated_fields(self) -> None:
        for calculator in self.get_field_calculators():
            calculator()

    def run_services(self) -> None:
        """Run the services needed on save(). Override if necessary."""

    def save(self, *args, **kwargs) -> None:
        self.update_calculated_fields()
        self.run_services()
        super().save(*args, **kwargs)


class TimeStampedMixin(models.Model):
    """Mixin with auto fields for the record's creation and modification dates."""

    created_at = models.DateTimeField(_("Дата создания записи"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Дата изменения записи"), auto_now=True)

    class Meta:
        abstract = True


class IsActiveMixin(models.Model):
    """Mixin with a record activity flag."""

    is_active = models.BooleanField(_("Активна"), default=True)

    class Meta:
        abstract = True


class UUIDModel(DefaultModel):
    """Base model with a UUID primary key."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class MoneyField(models.DecimalField):
    """DecimalField with defaults for storing monetary amounts."""

    def __init__(self, *args, **kwargs) -> None:
        kwargs.update(max_digits=10, decimal_places=2)
        super().__init__(*args, **kwargs)

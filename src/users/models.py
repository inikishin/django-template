from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self) -> str:
        return self.full_name or self.username

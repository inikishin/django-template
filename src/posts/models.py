from django.db import models
from django.utils.translation import gettext_lazy as _
from pytils.translit import slugify

from app.models import IsActiveMixin, TimeStampedMixin, UUIDModel
from users.models import User


class Tag(UUIDModel, TimeStampedMixin, IsActiveMixin):
    name = models.CharField(_("Название"), max_length=255, unique=True)

    class Meta:
        verbose_name = _("Тег")
        verbose_name_plural = _("Теги")


class PostQuerySet(models.QuerySet):
    """Reusable queries for Post (repository pattern)."""

    def published(self) -> "PostQuerySet":
        return self.filter(is_draft=False)


class Post(UUIDModel, TimeStampedMixin):
    class Language(models.TextChoices):
        RUSSIAN = "ru", _("Русский")
        ENGLISH = "en", _("Английский")

    title = models.CharField(_("Заголовок"), max_length=255)
    description = models.TextField(_("Описание"), blank=True, null=True)
    slug = models.SlugField(_("Slug"), max_length=350, unique=True, blank=True)
    content = models.TextField(_("Текст"))
    author = models.ForeignKey(
        User,
        verbose_name=_("Автор"),
        related_name="posts",
        on_delete=models.CASCADE,
    )
    language = models.CharField(
        _("Язык"),
        max_length=8,
        choices=Language.choices,
        default=Language.RUSSIAN,
    )
    is_draft = models.BooleanField(_("Черновик"), default=True)
    tags = models.ManyToManyField(
        Tag,
        verbose_name=_("Теги"),
        related_name="posts",
        blank=True,
    )

    objects = models.Manager.from_queryset(PostQuerySet)()

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = _("Статья")
        verbose_name_plural = _("Статьи")

    def __str__(self) -> str:
        return self.title

    def calculate_slug(self) -> None:
        """Fill the slug from the title (called automatically on save())."""
        if self.title:
            self.slug = slugify(self.title)

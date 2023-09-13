from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext as _

from users.models import User
from config.models import UUIDIdMixin, TimeStampedMixin, IsActiveMixin


class Tag(UUIDIdMixin, TimeStampedMixin, IsActiveMixin):
    name = models.CharField(verbose_name=_("Название"), unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Тег")
        verbose_name_plural = _("Теги")


class Post(UUIDIdMixin, TimeStampedMixin):
    class Language(models.TextChoices):
        RUSSIAN_LANG = 'ru', 'Russian'
        ENGLISH_LANG = 'en', 'English'

    title = models.CharField(verbose_name=_("Заголовок title для страницы"), max_length=255)
    description = models.TextField(verbose_name=_("Описание"), blank=True, null=True)
    header = models.CharField(verbose_name=_("Заголовок"), max_length=250)
    image_url = models.ImageField(verbose_name=_("Картинка"), blank=True, null=True)
    slug = models.SlugField(verbose_name=_("slug"), unique=True, blank=True)
    content = models.TextField(verbose_name=_("Текст"))
    author = models.ForeignKey(User,
                               verbose_name=_("Автор"),
                               related_name='posts',
                               on_delete=models.CASCADE)
    language = models.CharField(verbose_name=_("Язык"),
                                max_length=32,
                                choices=Language.choices,
                                default=Language.RUSSIAN_LANG)
    is_draft = models.BooleanField(verbose_name=_("Черновик"), default=True)
    tags = models.ManyToManyField(Tag,
                                  verbose_name=_("Теги"),
                                  blank=True,
                                  related_name="posts")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Post, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("Статья")
        verbose_name_plural = _("Статьи")

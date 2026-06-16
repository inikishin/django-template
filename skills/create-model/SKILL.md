---
name: create-model
description: >-
  Добавление или изменение модели Django в этом микросервисе по конвенциям проекта:
  наследование от DefaultModel/UUIDModel и миксин, русские verbose_name, вычисляемые
  поля через calculate_*, хук run_services, паттерн репозитория, миграции, регистрация
  в админке. Используй при создании новой модели, добавлении полей, заведении
  справочника или связи. Ключевые слова: модель, model, поле, миграция, makemigrations,
  ForeignKey, ManyToMany, справочник.
metadata:
  type: project-convention
  language: ru
---

# Создание модели

Перед изменениями свериться со структурой проекта (скил `project-structure`):
модели живут в `<app>/models.py`.

## 1. Выбрать базовый класс

Все модели наследуются от базовых классов из `app.models`:

- `DefaultModel` — обычная модель (PK — bigint). Даёт `__str__` по полю `name`,
  хуки `calculate_*` и `run_services()`, `update_from_kwargs`, `setattr_and_save`.
- `UUIDModel` — то же, но первичный ключ — UUID.

Добавляем миксины при необходимости:

- `TimeStampedMixin` — поля `created_at`, `updated_at`.
- `IsActiveMixin` — поле `is_active` (для справочников).

```python
from django.db import models
from django.utils.translation import gettext_lazy as _

from app.models import IsActiveMixin, TimeStampedMixin, UUIDModel
from users.models import User
```

## 2. Описать поля по конвенциям

- Первый позиционный аргумент `verbose_name` — на русском через `_()`.
- Варианты значений — через `models.TextChoices`.
- У `ForeignKey`/`ManyToManyField` указываем `verbose_name`, `related_name`,
  `on_delete`.
- Денежные суммы — `app.models.MoneyField`.

```python
class Tag(UUIDModel, TimeStampedMixin, IsActiveMixin):
    name = models.CharField(_("Название"), max_length=255, unique=True)

    class Meta:
        verbose_name = _("Тег")
        verbose_name_plural = _("Теги")


class Post(UUIDModel, TimeStampedMixin):
    class Language(models.TextChoices):
        RUSSIAN = "ru", _("Русский")
        ENGLISH = "en", _("Английский")

    title = models.CharField(_("Заголовок"), max_length=255)
    slug = models.SlugField(_("Slug"), max_length=350, unique=True, blank=True)
    content = models.TextField(_("Текст"))
    author = models.ForeignKey(
        User,
        verbose_name=_("Автор"),
        related_name="posts",
        on_delete=models.CASCADE,
    )
    language = models.CharField(
        _("Язык"), max_length=8, choices=Language.choices, default=Language.RUSSIAN
    )
    is_draft = models.BooleanField(_("Черновик"), default=True)
    tags = models.ManyToManyField(Tag, verbose_name=_("Теги"), related_name="posts", blank=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = _("Статья")
        verbose_name_plural = _("Статьи")

    def __str__(self) -> str:
        return self.title
```

## 3. Вычисляемые поля и сервисы на save()

`DefaultModel.save()` автоматически вызывает все методы `calculate_<field>`
(заполнение вычисляемых полей в БД) и `run_services()` (побочные эффекты).
НЕ переопределяем `save()` без необходимости — используем хуки.

```python
def calculate_slug(self) -> None:
    """Fill the slug from the title (called automatically on save())."""
    if self.title:
        self.slug = slugify(self.title)
```

## 4. Паттерн «репозиторий»

Логику выборки выносим в кастомные QuerySet/Manager, а не размазываем по вьюсетам:

```python
class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_draft=False)


class Post(UUIDModel, TimeStampedMixin):
    objects = models.Manager.from_queryset(PostQuerySet)()
    ...
```

## 5. Миграции

```bash
cd src && python manage.py makemigrations
cd src && python manage.py migrate
```

## 6. Админка

Каждую модель регистрируем в `<app>/admin.py` через `@admin.register(Model)`. Дефолтный
набор атрибутов:

- `list_display` — `id` + ключевые поля + временные метки (`created_at`/`updated_at`).
- `list_filter` — булевы поля, choices, FK, даты (`is_active`, статус, `updated_at` ...).
- `search_fields` — текстовые поля (`name`/`title`/`description`; по связям — `author__username`).

```python
from django.contrib import admin

from posts.models import Post, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "is_active", "created_at", "updated_at"]
    list_filter = ["is_active"]
    search_fields = ["name"]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "author", "language", "is_draft", "updated_at"]
    list_filter = ["language", "is_draft", "updated_at", "tags"]
    search_fields = ["title", "description"]
```

Дополнительно, по необходимости:

- `list_select_related = ["author"]` — против N+1 для FK, попавших в `list_display`.
- `autocomplete_fields = ["author", "tags"]` — для FK/M2M (требует `search_fields` в
  админке связанной модели).
- `readonly_fields = ["created_at", "updated_at"]` — чтобы показать авто-поля на странице.
- `date_hierarchy = "created_at"`, `ordering` — навигация/сортировка.
- Для rich-text-полей подключается форма с TinyMCE — см. фичу rich text в `initial-setup`.

## Чек-лист

- [ ] Наследование от `DefaultModel`/`UUIDModel` (+ миксины).
- [ ] `verbose_name` на русском, `Meta.verbose_name(_plural)`.
- [ ] `__str__` (если нет поля `name`).
- [ ] FK/M2M: `related_name`, `on_delete`, `verbose_name`.
- [ ] Вычисляемые поля — через `calculate_*`, не через `save()`.
- [ ] Созданы и применены миграции.
- [ ] Модель в админке.
- [ ] Есть тесты (скил `backend-testing`).

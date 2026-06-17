---
name: create-model
description: >-
  Adding or changing a Django model in this microservice per project conventions:
  inheriting from DefaultModel/UUIDModel and mixins, Russian verbose_name, computed
  fields via calculate_*, the run_services hook, the repository pattern, migrations,
  admin registration. Use when creating a new model, adding fields, setting up a
  lookup table or a relation. Keywords: модель, model, поле, миграция, makemigrations,
  ForeignKey, ManyToMany, справочник.
metadata:
  type: project-convention
  language: en
---

# Creating a model

Before making changes, check against the project structure (skill `project-structure`):
models live in `<app>/models.py`.

## 1. Pick a base class

All models inherit from base classes in `app.models`:

- `DefaultModel` — a regular model (PK is bigint). Provides `__str__` from the `name`
  field, the `calculate_*` and `run_services()` hooks, `update_from_kwargs`, `setattr_and_save`.
- `UUIDModel` — the same, but the primary key is a UUID.

Add mixins as needed:

- `TimeStampedMixin` — `created_at`, `updated_at` fields.
- `IsActiveMixin` — `is_active` field (for lookup tables).

```python
from django.db import models
from django.utils.translation import gettext_lazy as _

from app.models import IsActiveMixin, TimeStampedMixin, UUIDModel
from users.models import User
```

## 2. Define fields per conventions

- The first positional argument `verbose_name` — in Russian via `_()`.
- Choices — via `models.TextChoices`.
- For `ForeignKey`/`ManyToManyField` specify `verbose_name`, `related_name`,
  `on_delete`.
- Money amounts — `app.models.MoneyField`.

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

## 3. Computed fields and services on save()

`DefaultModel.save()` automatically calls all `calculate_<field>` methods
(filling computed fields in the DB) and `run_services()` (side effects).
Do NOT override `save()` unless necessary — use the hooks.

```python
def calculate_slug(self) -> None:
    """Fill the slug from the title (called automatically on save())."""
    if self.title:
        self.slug = slugify(self.title)
```

## 4. Repository pattern

Move query logic into custom QuerySet/Manager classes instead of spreading it across viewsets:

```python
class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_draft=False)


class Post(UUIDModel, TimeStampedMixin):
    objects = models.Manager.from_queryset(PostQuerySet)()
    ...
```

## 5. Migrations

```bash
cd src && python manage.py makemigrations
cd src && python manage.py migrate
```

## 6. Admin

Register every model in `<app>/admin.py` via `@admin.register(Model)`. The default
set of attributes:

- `list_display` — `id` + key fields + timestamps (`created_at`/`updated_at`).
- `list_filter` — boolean fields, choices, FKs, dates (`is_active`, status, `updated_at` ...).
- `search_fields` — text fields (`name`/`title`/`description`; across relations — `author__username`).

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

Additionally, as needed:

- `list_select_related = ["author"]` — against N+1 for FKs that appear in `list_display`.
- `autocomplete_fields = ["author", "tags"]` — for FK/M2M (requires `search_fields` in
  the related model's admin).
- `readonly_fields = ["created_at", "updated_at"]` — to show auto-fields on the page.
- `date_hierarchy = "created_at"`, `ordering` — navigation/sorting.
- For rich-text fields a TinyMCE form is wired in — see the rich text feature in `initial-setup`.

## Checklist

- [ ] Inheritance from `DefaultModel`/`UUIDModel` (+ mixins).
- [ ] `verbose_name` in Russian, `Meta.verbose_name(_plural)`.
- [ ] `__str__` (if there is no `name` field).
- [ ] FK/M2M: `related_name`, `on_delete`, `verbose_name`.
- [ ] Computed fields — via `calculate_*`, not via `save()`.
- [ ] Migrations created and applied.
- [ ] Model in the admin.
- [ ] Tests exist (skill `backend-testing`).

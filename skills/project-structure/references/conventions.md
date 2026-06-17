# Code conventions

A rule set from the reference project. The rules are an experienced advisor, not a
strict law: any of them may be broken given a rock-solid argument. We follow them not
for the rules' sake but for the sake of flexible, loosely coupled code (DRY, KISS).

## PEP8 and formatting

- Aim for PEP8, except line length: the limit is **120** characters.
- Formatter — ruff (`ruff format`, a black equivalent). Quotes are **double**.
- Lint: `make lint` (pre-commit with ruff + ruff-format).

## Imports

- isort, black profile. Three blocks (stdlib / third-party / local).
- Import entities from outside stdlib by name (list the classes/functions).
  Import stdlib modules as whole modules. `import *` — not allowed. Resolve collisions with `as`.

```python
import collections
from posts.models import Post
```

## Formatting calls

- Fits on a line — write it on one line.
- Doesn't fit — wrap after the opening parenthesis.
- Many arguments / nesting — expanded formatting, closing parenthesis
  on its own line without extra indentation.

## Commas

- In multiline listings (lists, calls, tuples) — a trailing comma after the
  last element.
- In single-line ones — no trailing comma. Exception: a single-element tuple `(1,)`.

## Function arguments

Name the arguments when they are not obvious from the function name:

```python
serializer.is_valid(raise_exception=True)
```

## Comments and docstrings

- Comments — where the code does something non-obvious; do not restate the code in words.
- A single-line docstring ends with a period, with no line breaks:
  `"""Computing predecessors for tasks."""`
- Multiline: the first line — the gist with a period, a blank line, then the body. No indentation
  from the quotes.
- Inline comments — for implicit cases and references to tickets (`# more in BES-482`).
- TODO/FIXME are fine while working, but clean them up before a commit (fix or file a ticket).

## Logging

All logs — in English (library logs are English too, we need consistency):

```python
logger.info("Requesting balance")
```

## Unused code

Remove everything we can: commented-out code, obsolete features, one-off scripts.
No code — no bugs.

## The "repository" pattern for models

Move filtering and query methods into custom QuerySet and Manager classes:

```python
from django.db import models
from django.db.models import QuerySet


class PostQuerySet(QuerySet):
    def published(self) -> "PostQuerySet":
        return self.filter(is_draft=False)

    def by_author(self, author_id) -> "PostQuerySet":
        return self.filter(author_id=author_id)


class PostManager(models.Manager):
    def create_published(self, **kwargs):
        return self.create(is_draft=False, **kwargs)


class Post(DefaultModel):
    objects = PostManager.from_queryset(PostQuerySet)()
```

In viewsets and services use `Post.objects.published()` instead of
`Post.objects.filter(is_draft=False)`.

## Language

- **Comments and docstrings — in English only.** This is mandatory for all code
  and related files (configs, Dockerfile, Makefile, etc.).
- Logs, variable/function/class names — English.
- Russian remains only for user-facing text: `verbose_name`,
  `help_text`, `summary`/`description` in the schema, validation messages — via
  `from django.utils.translation import gettext_lazy as _`.

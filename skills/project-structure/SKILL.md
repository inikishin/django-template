---
name: project-structure
description: >-
  Map of the Django + DRF microservice project structure (this template): where
  settings, base classes, apps, the API, and tests live, and which conventions to
  follow. Use it ALWAYS before making changes to the project — to put code in the
  right place and not break the style. Keywords: project structure, where to put a
  file, where the settings are, new app, code conventions, app/, api/, settings.
metadata:
  type: project-convention
  language: en
---

# Project structure and conventions

A Django + DRF microservice. All Python code lives in the `src/` directory.
The core (base classes and settings) is the `app/` package. Business logic lives in
separate Django apps.

## Directory tree

Repository-level configuration (env, pytest, docker, linter) lives at the ROOT, while
all Python code lives in `src/`.

```
.                            # repo root
├── .env                     # environment variables (do NOT commit; .env.example sits alongside)
├── pytest.ini               # pytest config (pythonpath=src, testpaths=src)
├── Makefile, ruff.toml, .pre-commit-config.yaml
├── Dockerfile, docker-compose.yml
├── requirements.txt, dev-requirements.txt
├── scripts/                 # helper scripts (entrypoint.sh, etc.)
├── skills/                   # template skills (moved into .claude/ during setup)
├── fixtures/                 # JSON fixture dumps of test data (loaded by the load_data fixture)
├── db.sqlite3                # default DB (in .gitignore); staticfiles/, media/ live here too
└── src/                      # ONLY python code
    ├── manage.py
    ├── conftest.py              # thin: re-exports fixtures from app.tests.fixtures
    ├── app/                     # CORE: reusable classes + settings (also a Django app)
    │   ├── settings.py          # thin: SECRET_KEY, DEBUG, include(config/*)
    │   ├── urls.py              # root urlconf (admin, swagger, api_urlpatterns)
    │   ├── config/              # split-settings: api, auth, db, http, i18n, ... (cache/celery - optional)
    │   ├── api/                 # reusable API elements (inherited from in apps)
    │   │   ├── viewsets.py      #   DefaultModelViewSet, ReadonlyModelViewSet, mixins
    │   │   ├── serializers.py   #   ReadOnlyModelSerializer
    │   │   ├── filtersets.py    #   SearchFilterSet
    │   │   ├── routers.py       #   DefaultRouter (DELETE on a list -> bulk_delete)
    │   │   ├── pagination.py    #   StandardResultsSetPagination (page/page_size)
    │   │   └── permissions.py   #   IsAuthenticated, ReadOnly
    │   ├── models.py            # ONLY mixins/base classes (DefaultModel, UUIDModel, ...); no models
    │   ├── tests/               # shared test objects: api.py (ApiClient), fixtures.py, loaddata.py
    │   ├── wsgi.py / asgi.py
    │   └── apps.py
    └── <app>/                  # posts - example (delete it); users - custom User (core)
        ├── models.py            # models + QuerySet/Manager (repository pattern)
        ├── constants.py         # app constants
        ├── admin.py
        ├── apps.py
        ├── urls.py              # DefaultRouter + path()
        ├── api/                 # presentation layer (HTTP); NO business logic
        │   ├── viewsets.py      #   views/viewsets: request handling, validation, response
        │   ├── serializers.py   #   serializers
        │   ├── filtersets.py    #   django-filter settings
        │   └── schema.py        #   extend_schema descriptors for swagger
        ├── services/            # business logic: class-based services (called from views/admin/CLI/tasks)
        ├── tasks/               # Celery tasks (if the feature is enabled)
        ├── tests/               # tests + fixtures/factories
        │   ├── conftest.py      #   app fixtures/factories (optional, only if there are any)
        │   ├── api/             #   endpoint tests
        │   └── services/        #   business-logic tests
        └── migrations/
```

## App layers

A clear separation of responsibilities:

- **`models.py`** — data. Move reusable querysets into custom
  `QuerySet`/`Manager` classes (repository pattern): `Post.objects.published()`.
- **`services/`** — business logic. A separate layer; called from views, admin
  actions, CLI commands, Celery tasks. Write them as **class-based services** (even with
  a single method) — see the `generate-api-method` skill.
- **`api/` (viewsets)** — the HTTP layer. Only request handling, validation (via
  serializers), calling a service, and building the response. **No business logic.**
- **`constants.py`** — app constants (import them wherever needed).

Example: the `posts` viewset in the `@action similar` only calls `SimilarPostsService(post)()`
and returns the response; the DB query itself lives in the service, and `published()` — in `PostQuerySet`.

## Where to put what

| What we add | Where |
| --- | --- |
| Model | `<app>/models.py` (see the create-model skill) |
| Business logic | `<app>/services/` (called from views/admin/CLI/tasks) |
| App constant | `<app>/constants.py` |
| Endpoint / ViewSet / @action | `<app>/api/viewsets.py` (thin; call logic from `services/`) (see generate-api-method) |
| Serializer | `<app>/api/serializers.py` |
| Filter / search | `<app>/api/filtersets.py` (inherit `SearchFilterSet`) |
| Swagger description | `<app>/api/schema.py` |
| App routes | `<app>/urls.py`, then add to the `api_urlpatterns` list in `app/urls.py` |
| Test | `<app>/tests/api/` or `<app>/tests/services/` (see backend-testing) |
| App fixture/factory (if any) | `<app>/tests/conftest.py` (create only if you have your own fixtures) |
| Shared (across all apps) fixture | `app/tests/fixtures.py` (re-exported in `src/conftest.py`) |
| Django setting | the relevant module in `app/config/` (NOT in `settings.py`) |
| Celery task (if the feature is enabled) | `<app>/tasks/` (a package; autodiscovered; see `initial-setup`) |
| Base class shared across all apps | `app/...` |

## The `app/` package (core) — rules

`app/` is the main application with the service's settings and reusable elements.

- **`api/`** — what is reused in other apps (inherited from): pagination,
  base serializers/views/viewsets/router/permissions. No concrete endpoints here.
- **`config/`** — pluggable settings modules (split-settings); included via
  `include(...)` in `app/settings.py`. Change a setting in the relevant module, not in `settings.py`.
- **`tests/`** — shared test objects: `api.py` (`ApiClient`), `fixtures.py` (shared
  fixtures + `__all__`), `loaddata.py` (the `load_data` fixture loads JSON dumps from
  `fixtures/`). The test data dumps themselves — in `fixtures/*.json`.
- **`urls.py`** — a single file: the root urlconf (admin, swagger/redoc/schema) and the
  `api_urlpatterns` list with the apps' routes. There is no separate `urls/` package.
- **`models.py`** — ONLY mixins and base classes for inheritance
  (`DefaultModel`, `UUIDModel`, `TimeStampedMixin`, `IsActiveMixin`, `MoneyField`).
  No concrete models are created in `app/`.

## Base classes (always inherit from them)

- Models: `app.models.DefaultModel` / `UUIDModel` (+ mixins `TimeStampedMixin`, `IsActiveMixin`).
- ViewSet: `app.api.viewsets.DefaultModelViewSet` (CRUD) / `ReadonlyModelViewSet` (read-only).
- FilterSet: `app.api.filtersets.SearchFilterSet`.
- Router: `app.api.routers.DefaultRouter`.
- In tests: `app.tests.ApiClient`; loading dumps — the `load_data` fixture (see backend-testing).

## New app

1. `cd src && python manage.py startapp <name>`, then bring it to the structure above:
   create `api/` (`viewsets.py`/`serializers.py`/`filtersets.py`/`schema.py`), `tests/`
   and, as needed, `services/`, `constants.py`, `tasks/`.
2. Add `"<name>"` to `LOCAL_APPS` in `app/config/installed_apps.py`.
3. Wire up `path("<name>/", include("<name>.urls"))` in `app/urls.py`.

## Code conventions (from the reference project)

The detailed rule set is in [references/conventions.md](references/conventions.md). In brief:

- Formatting: ruff (a black equivalent), line length **120**, **double** quotes.
- Imports: isort, 3 blocks (stdlib / third-party / local); import entities by name,
  stdlib modules — as whole modules; `import *` is forbidden.
- Multiline listings — with a trailing comma after the last element.
- In `__init__.py` — imports only.
- `verbose_name` and user-facing text — in Russian via `gettext_lazy as _`.
- Logs — in English.
- A single-line docstring ends with a period.
- Move filters and querysets into custom QuerySet/Manager classes (the "repository" pattern).
- Remove dead/commented-out code; do not leave TODO/FIXME in a commit.

## Related skills

- Models — `create-model`.
- Endpoints — `generate-api-method`.
- Tests — `backend-testing`.
- Setup/run/troubleshooting — `initial-setup`.

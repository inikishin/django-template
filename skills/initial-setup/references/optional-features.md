# Project optional features

The template is minimal by default. The feature set is configurable: during initial setup
FIRST ask the user the questions (below), then wire in the chosen variants. Come back to this
same skill when you need to SWITCH the approach later.

Principle: each feature is a separate split-settings file in `app/config/`, wired into
`include(...)` in `app/settings.py` only when needed. Ready-made template files live
in `assets/` of this skill; "snippets" (a few lines into an existing file) are given here.

## Questions and default values

| Feature | Default | Variants |
| --- | --- | --- |
| 1. Database | sqlite | sqlite / postgres |
| 2. Authentication | no authentication | no authentication / jwt / oauth / keycloak |
| 3. Throttling (rate limiting) | no | no / yes |
| 4. i18n (internationalization) | no | no / yes |
| 5. Static and media storage | Django server | server / s3 |
| 6. Rich text | no | no / yes (tinymce) |
| 7. Cache | no (locmem) | no / Redis |
| 8. Background tasks (Celery) | no | no / yes |

The current base is already assembled with the "default" values. Below is how to enable the
other variants (and how to return to the default).

---

## 1. Database

- **sqlite** (default): the current `app/config/db.py` (the `db.sqlite3` file, no dependencies).
- **postgres**:
  1. dep: `psycopg2-binary==2.9.12` in `requirements.txt`.
  2. `assets/db/postgres.py` → `src/app/config/db.py`.
  3. env in `.env`/`.env.example`:
     ```
     DB_HOST=localhost
     DB_PORT=5432
     DB_NAME=<name>
     DB_USER=postgres
     DB_PASS=postgres
     ```
  4. docker-compose: add a `db` (postgres) service and in `django` pass `DB_HOST: db`
     + `depends_on: [db]`:
     ```yaml
       db:
         image: postgres:15
         environment:
           POSTGRES_DB: ${DB_NAME}
           POSTGRES_USER: ${DB_USER}
           POSTGRES_PASSWORD: ${DB_PASS}
         volumes:
           - pg_data:/var/lib/postgresql/data
         ports:
           - "5432:5432"
     # ... and at the bottom of the file:
     volumes:
       pg_data:
     ```

## 2. Authentication

- **no authentication** (default): in `app/config/api.py` `REST_FRAMEWORK`
  `DEFAULT_AUTHENTICATION_CLASSES = ()`, `DEFAULT_PERMISSION_CLASSES = (AllowAny,)`.
- **jwt** (djangorestframework-simplejwt):
  1. dep: `djangorestframework-simplejwt==5.5.1` in `requirements.txt`.
  2. `assets/auth/jwt/conf_jwt.py` → `src/app/config/jwt.py`; add `"config/jwt.py"` to `include(...)`.
  3. In `app/config/api.py` replace the access settings:
     ```python
     "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
     "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
     ```
  4. Create the `src/auth/` app from `assets/auth/jwt/auth_app/` (`views.py`, `urls.py`,
     `serializers.py`) + an empty `__init__.py`.
  5. In `app/urls.py` add the route: `path("auth/", include("auth.urls"))`.
  6. Test (example): login returns `access`/`refresh`, refresh renews `access`.
- **keycloak** (drf-keycloak-auth, as in the reference project):
  1. dep: `drf-keycloak-auth==0.1.0`.
  2. `assets/auth/keycloak/conf_keycloak.py` → `src/app/config/keycloak.py`; add
     `"config/keycloak.py"` to `include(...)`.
  3. In `REST_FRAMEWORK` (`app/config/api.py`):
     ```python
     "DEFAULT_AUTHENTICATION_CLASSES": ("drf_keycloak_auth.authentication.KeycloakAuthentication",),
     "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
     ```
  4. env: `KEYCLOAK_SERVER_URL`, `KEYCLOAK_REALM`, `KEYCLOAK_CLIENT_ID`,
     `KEYCLOAK_CLIENT_SECRET_KEY` (see the settings file).
  5. Integration details (role mapping, exempt-uri, etc.) will be added later following the
     reference project.
- **oauth** (django-oauth-toolkit) — guide, details to be added later:
  1. dep: `django-oauth-toolkit`.
  2. INSTALLED_APPS: `"oauth2_provider"`; `cd src && python manage.py migrate`.
  3. In `REST_FRAMEWORK`: `DEFAULT_AUTHENTICATION_CLASSES =
     ("oauth2_provider.contrib.rest_framework.OAuth2Authentication",)`,
     `DEFAULT_PERMISSION_CLASSES = ("rest_framework.permissions.IsAuthenticated",)`.
  4. In `app/urls.py`: `path("o/", include("oauth2_provider.urls", namespace="oauth2_provider"))`.

## 3. Throttling

- **no** (default).
- **yes**: add to `REST_FRAMEWORK` (`app/config/api.py`):
  ```python
  "DEFAULT_THROTTLE_CLASSES": (
      "rest_framework.throttling.AnonRateThrottle",
      "rest_framework.throttling.UserRateThrottle",
  ),
  "DEFAULT_THROTTLE_RATES": {
      "anon": "100/hour",
      "user": "1000/hour",
  },
  ```
  In tests throttling is usually disabled (e.g. via your own env flag or raised rates).

## 4. i18n (internationalization)

- **no** (default): the current `app/config/i18n.py` (language/timezone, no content translation).
- **yes**:
  1. `assets/i18n/i18n.py` → `src/app/config/i18n.py` (adds `LANGUAGES`, `LOCALE_PATHS`).
  2. In `app/config/middleware.py` add `"django.middleware.locale.LocaleMiddleware"`
     (after `SessionMiddleware`, before `CommonMiddleware`).
  3. Model field translation (optional, django-modeltranslation):
     - dep: `django-modeltranslation`;
     - in `app/config/installed_apps.py` add `"modeltranslation"` **before**
       `django.contrib.admin`;
     - create `src/<app>/translation.py` (example — `assets/i18n/translation_example.py`);
     - `makemigrations`/`migrate` for the translation fields; `makemessages`/`compilemessages`.
     - In tests: for translatable fields via `G()` specify `field_ru=...` (see the
       `backend-testing` skill).

## 5. Static and media storage

- **Django server** (default): `app/config/static.py` + `app/config/media.py` (locally).
- **s3** (django-storages):
  1. deps: `django-storages`, `boto3`.
  2. `assets/storage/s3.py` → `src/app/config/storage.py`; add `"config/storage.py"` to
     `include(...)` **after** `config/static.py`/`config/media.py`.
  3. INSTALLED_APPS: `"storages"`.
  4. env: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME`,
     `AWS_S3_ENDPOINT_URL`, `AWS_S3_REGION_NAME` (see the file).
  5. Swagger/ReDoc static is also served this way (sidecar) — removing the dependency on the local disk.

## 6. Rich text (tinymce)

- **no** (default): `Post.content` is a plain `TextField`.
- **yes** (django-tinymce):
  1. dep: `django-tinymce`.
  2. INSTALLED_APPS: `"tinymce"`.
  3. `assets/richtext/forms.py` → `src/posts/forms.py`.
  4. In `src/posts/admin.py`: `from posts.forms import PostAdminForm` and in `PostAdmin`
     add `form = PostAdminForm`.
  5. (Opt.) in `app/urls.py`: `path("tinymce/", include("tinymce.urls"))`.

## 7. Cache (Redis)

A distributed cache, shared across multiple gunicorn workers.

1. dep: `redis==8.0.0`.
2. `assets/cache/cache.py` → `src/app/config/cache.py`; add `"config/cache.py"` to `include(...)`.
3. env: `REDIS_URL=redis://localhost:6379/0`.
4. Tests: in `pytest.ini` add `USE_IN_MEMORY_CACHE=True` to the `env` block (locmem instead of Redis).
5. docker-compose: add a `redis` service and pass `REDIS_URL` into `django`
   (see the redis block in the Celery section — it's shared).

## 8. Background tasks (Celery)

Asynchronous and periodic tasks. Uses Redis as the broker (needed even without the cache).

1. deps: `celery==5.6.3`, `django-celery-beat==2.9.0`, `redis==8.0.0`, `flower==2.0.1`.
2. Copy from `assets/celery/`:
   - `app_celery.py` → `src/app/celery.py`
   - `conf_celery.py` → `src/app/config/celery.py`
   - `worker.sh`, `beat.sh`, `flower.sh` → `scripts/` (then `chmod +x`)
   - `tasks_example.py` → a task in the `src/<app>/tasks/` package (e.g. `tasks/example.py`;
     in `tasks/__init__.py` we import the tasks for autodiscovery)
3. In `src/app/__init__.py`:
   ```python
   from app.celery import app as celery_app

   __all__ = ["celery_app"]
   ```
4. In `app/settings.py` `include(...)`: `"config/celery.py"`.
5. In `app/config/installed_apps.py` (THIRD_PARTY_APPS): `"django_celery_beat"`.
6. env: `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`.
7. Tests: in `pytest.ini` `env` add `CELERY_ALWAYS_EAGER=True`.
8. `cd src && python manage.py migrate` (django_celery_beat migrations). Run: `sh scripts/worker.sh` /
   `beat.sh` / `flower.sh` (Flower — UI at http://localhost:5555).

### docker-compose (redis + workers)

```yaml
  redis:
    image: redis:7
    ports:
      - "6379:6379"

  celery_worker:
    build: .
    command: celery -A app worker -l info
    env_file:
      - .env
    environment:
      DB_HOST: db
      REDIS_URL: redis://redis:6379/0
      CELERY_BROKER_URL: redis://redis:6379/1
      CELERY_RESULT_BACKEND: redis://redis:6379/2
    depends_on:
      - db
      - redis

  celery_beat:
    build: .
    command: celery -A app beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    env_file:
      - .env
    environment:
      DB_HOST: db
      REDIS_URL: redis://redis:6379/0
      CELERY_BROKER_URL: redis://redis:6379/1
      CELERY_RESULT_BACKEND: redis://redis:6379/2
    depends_on:
      - db
      - redis
```

### The task and testing it

The task (`assets/celery/tasks_example.py`):
```python
from celery import shared_task


@shared_task
def example_task(x: int, y: int) -> int:
    """Example background task."""
    return x + y
```

Testing approaches (in decreasing order of preference):

1. **Thin task + test the logic directly (recommended).** Keep `@shared_task`
   thin — it only orchestrates, while the business logic is moved into a service/function (like
   querysets/services in our conventions) and tested without Celery:
   ```python
   def test_compute_logic():
       assert compute_sum(2, 3) == 5  # a plain function, Celery not needed
   ```

2. **Test the task itself in eager mode.** In tests `CELERY_ALWAYS_EAGER=True`, so
   `.delay()` runs synchronously — we check the task's "wiring" (argument
   serialization, that the task works at all); a real broker/retries are not covered by this:
   ```python
   from <app>.tasks import example_task


   def test_example_task():
       assert example_task.delay(2, 3).get() == 5
       # or a synchronous call without touching the broker:
       assert example_task.run(2, 3) == 5
   ```

3. **Mock when testing code that SCHEDULES a task.** When testing the calling
   code (a viewset/service that enqueues a task) — mock `.delay` and check that the
   task is scheduled with the right arguments; don't run the task itself:
   ```python
   from unittest.mock import patch


   def test_view_schedules_task(as_user):
       with patch("<app>.tasks.example_task.delay") as mock_delay:
           as_user.post("/api/...", data)
           mock_delay.assert_called_once_with(2, 3)
   ```

Rule: the less logic in the task itself, the less you need to run Celery in tests.

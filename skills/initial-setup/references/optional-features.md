# Опциональные фичи проекта

Шаблон по умолчанию минимален. Набор фич конфигурируется: при первичной настройке
СНАЧАЛА задай пользователю вопросы (ниже), затем подключи выбранные варианты. К этому
же скилу обращаемся, когда нужно ПЕРЕКЛЮЧИТЬ подход позже.

Принцип: каждая фича — отдельный split-settings файл в `app/config/`, подключаемый в
`include(...)` в `app/settings.py` только при необходимости. Готовые файлы-шаблоны лежат
в `assets/` этого скила; «снипеты» (несколько строк в существующий файл) приведены здесь.

## Вопросы и значения по умолчанию

| Фича | По умолчанию | Варианты |
| --- | --- | --- |
| 1. База данных | sqlite | sqlite / postgres |
| 2. Авторизация | без авторизации | без авторизации / jwt / oauth / keycloak |
| 3. Throttling (ограничение частоты) | нет | нет / да |
| 4. i18n (интернационализация) | нет | нет / да |
| 5. Хранение статики и медиа | сервер Django | сервер / s3 |
| 6. Rich text (форматированный текст) | нет | нет / да (tinymce) |
| 7. Кэш | нет (locmem) | нет / Redis |
| 8. Фоновые задачи (Celery) | нет | нет / да |

Текущая база уже собрана по значениям «по умолчанию». Ниже — как включить остальные
варианты (и как вернуться к дефолту).

---

## 1. База данных

- **sqlite** (по умолчанию): текущий `app/config/db.py` (файл `db.sqlite3`, без зависимостей).
- **postgres**:
  1. dep: `psycopg2-binary==2.9.12` в `requirements.txt`.
  2. `assets/db/postgres.py` → `src/app/config/db.py`.
  3. env в `.env`/`.env.example`:
     ```
     DB_HOST=localhost
     DB_PORT=5432
     DB_NAME=<name>
     DB_USER=postgres
     DB_PASS=postgres
     ```
  4. docker-compose: добавить сервис `db` (postgres) и в `django` пробросить `DB_HOST: db`
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
     # ... и внизу файла:
     volumes:
       pg_data:
     ```

## 2. Авторизация

- **без авторизации** (по умолчанию): в `app/config/api.py` `REST_FRAMEWORK`
  `DEFAULT_AUTHENTICATION_CLASSES = ()`, `DEFAULT_PERMISSION_CLASSES = (AllowAny,)`.
- **jwt** (djangorestframework-simplejwt):
  1. dep: `djangorestframework-simplejwt==5.5.1` в `requirements.txt`.
  2. `assets/auth/jwt/conf_jwt.py` → `src/app/config/jwt.py`; добавить `"config/jwt.py"` в `include(...)`.
  3. В `app/config/api.py` заменить настройки доступа:
     ```python
     "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
     "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
     ```
  4. Создать приложение `src/auth/` из `assets/auth/jwt/auth_app/` (`views.py`, `urls.py`,
     `serializers.py`) + пустой `__init__.py`.
  5. В `app/urls.py` добавить маршрут: `path("auth/", include("auth.urls"))`.
  6. Тест (пример): логин возвращает `access`/`refresh`, refresh обновляет `access`.
- **keycloak** (drf-keycloak-auth, как в эталонном проекте):
  1. dep: `drf-keycloak-auth==0.1.0`.
  2. `assets/auth/keycloak/conf_keycloak.py` → `src/app/config/keycloak.py`; добавить
     `"config/keycloak.py"` в `include(...)`.
  3. В `REST_FRAMEWORK` (`app/config/api.py`):
     ```python
     "DEFAULT_AUTHENTICATION_CLASSES": ("drf_keycloak_auth.authentication.KeycloakAuthentication",),
     "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
     ```
  4. env: `KEYCLOAK_SERVER_URL`, `KEYCLOAK_REALM`, `KEYCLOAK_CLIENT_ID`,
     `KEYCLOAK_CLIENT_SECRET_KEY` (см. файл настроек).
  5. Детали интеграции (маппинг ролей, exempt-uri и т.п.) добавим позже по образцу
     эталонного проекта.
- **oauth** (django-oauth-toolkit) — гайд, детали добавим позже:
  1. dep: `django-oauth-toolkit`.
  2. INSTALLED_APPS: `"oauth2_provider"`; `cd src && python manage.py migrate`.
  3. В `REST_FRAMEWORK`: `DEFAULT_AUTHENTICATION_CLASSES =
     ("oauth2_provider.contrib.rest_framework.OAuth2Authentication",)`,
     `DEFAULT_PERMISSION_CLASSES = ("rest_framework.permissions.IsAuthenticated",)`.
  4. В `app/urls.py`: `path("o/", include("oauth2_provider.urls", namespace="oauth2_provider"))`.

## 3. Throttling

- **нет** (по умолчанию).
- **да**: добавить в `REST_FRAMEWORK` (`app/config/api.py`):
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
  В тестах throttling обычно отключают (например, своим env-флагом или повышенными rates).

## 4. i18n (интернационализация)

- **нет** (по умолчанию): текущий `app/config/i18n.py` (язык/таймзона, без перевода контента).
- **да**:
  1. `assets/i18n/i18n.py` → `src/app/config/i18n.py` (добавляет `LANGUAGES`, `LOCALE_PATHS`).
  2. В `app/config/middleware.py` добавить `"django.middleware.locale.LocaleMiddleware"`
     (после `SessionMiddleware`, перед `CommonMiddleware`).
  3. Перевод полей моделей (опционально, django-modeltranslation):
     - dep: `django-modeltranslation`;
     - в `app/config/installed_apps.py` добавить `"modeltranslation"` **перед**
       `django.contrib.admin`;
     - создать `src/<app>/translation.py` (пример — `assets/i18n/translation_example.py`);
     - `makemigrations`/`migrate` для полей перевода; `makemessages`/`compilemessages`.
     - В тестах: для переводимых полей через `G()` указывать `field_ru=...` (см. скил
       `backend-testing`).

## 5. Хранение статики и медиа

- **сервер Django** (по умолчанию): `app/config/static.py` + `app/config/media.py` (локально).
- **s3** (django-storages):
  1. deps: `django-storages`, `boto3`.
  2. `assets/storage/s3.py` → `src/app/config/storage.py`; добавить `"config/storage.py"` в
     `include(...)` **после** `config/static.py`/`config/media.py`.
  3. INSTALLED_APPS: `"storages"`.
  4. env: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME`,
     `AWS_S3_ENDPOINT_URL`, `AWS_S3_REGION_NAME` (см. файл).
  5. Так же отдаётся статика Swagger/ReDoc (sidecar) — снимает зависимость от локального диска.

## 6. Rich text (tinymce)

- **нет** (по умолчанию): `Post.content` — обычный `TextField`.
- **да** (django-tinymce):
  1. dep: `django-tinymce`.
  2. INSTALLED_APPS: `"tinymce"`.
  3. `assets/richtext/forms.py` → `src/posts/forms.py`.
  4. В `src/posts/admin.py`: `from posts.forms import PostAdminForm` и в `PostAdmin`
     добавить `form = PostAdminForm`.
  5. (Опц.) в `app/urls.py`: `path("tinymce/", include("tinymce.urls"))`.

## 7. Кэш (Redis)

Распределённый кэш, общий для нескольких воркеров gunicorn.

1. dep: `redis==8.0.0`.
2. `assets/cache/cache.py` → `src/app/config/cache.py`; добавить `"config/cache.py"` в `include(...)`.
3. env: `REDIS_URL=redis://localhost:6379/0`.
4. Тесты: в `pytest.ini` в блок `env` добавить `USE_IN_MEMORY_CACHE=True` (locmem вместо Redis).
5. docker-compose: добавить сервис `redis` и пробросить `REDIS_URL` в `django`
   (см. блок redis в разделе Celery — он общий).

## 8. Фоновые задачи (Celery)

Асинхронные и периодические задачи. Использует Redis как брокер (нужен даже без кэша).

1. deps: `celery==5.6.3`, `django-celery-beat==2.9.0`, `redis==8.0.0`, `flower==2.0.1`.
2. Скопировать из `assets/celery/`:
   - `app_celery.py` → `src/app/celery.py`
   - `conf_celery.py` → `src/app/config/celery.py`
   - `worker.sh`, `beat.sh`, `flower.sh` → `scripts/` (затем `chmod +x`)
   - `tasks_example.py` → задача в пакете `src/<app>/tasks/` (напр. `tasks/example.py`;
     в `tasks/__init__.py` импортируем задачи для автодискавера)
3. В `src/app/__init__.py`:
   ```python
   from app.celery import app as celery_app

   __all__ = ["celery_app"]
   ```
4. В `app/settings.py` `include(...)`: `"config/celery.py"`.
5. В `app/config/installed_apps.py` (THIRD_PARTY_APPS): `"django_celery_beat"`.
6. env: `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`.
7. Тесты: в `pytest.ini` `env` добавить `CELERY_ALWAYS_EAGER=True`.
8. `cd src && python manage.py migrate` (миграции django_celery_beat). Запуск: `sh scripts/worker.sh` /
   `beat.sh` / `flower.sh` (Flower — UI на http://localhost:5555).

### docker-compose (redis + воркеры)

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

### Задача и её тестирование

Задача (`assets/celery/tasks_example.py`):
```python
from celery import shared_task


@shared_task
def example_task(x: int, y: int) -> int:
    """Example background task."""
    return x + y
```

Подходы к тестированию (по убыванию предпочтения):

1. **Тонкая задача + тест логики напрямую (рекомендуется).** `@shared_task` держим
   тонким — он только оркестрирует, а бизнес-логику выносим в сервис/функцию (как
   querysets/services в наших конвенциях) и тестируем её без Celery:
   ```python
   def test_compute_logic():
       assert compute_sum(2, 3) == 5  # обычная функция, Celery не нужен
   ```

2. **Тест самой задачи в eager-режиме.** В тестах `CELERY_ALWAYS_EAGER=True`, поэтому
   `.delay()` выполняется синхронно — проверяем «обвязку» задачи (сериализация
   аргументов, что задача в принципе работает); реальный брокер/ретраи это не покрывает:
   ```python
   from <app>.tasks import example_task


   def test_example_task():
       assert example_task.delay(2, 3).get() == 5
       # либо синхронный вызов без обращения к брокеру:
       assert example_task.run(2, 3) == 5
   ```

3. **Мок при тестировании кода, который ПЛАНИРУЕТ задачу.** Когда тестируем вызывающий
   код (вьюсет/сервис, ставящий задачу в очередь) — мокаем `.delay` и проверяем, что
   задача запланирована с нужными аргументами; саму задачу не выполняем:
   ```python
   from unittest.mock import patch


   def test_view_schedules_task(as_user):
       with patch("<app>.tasks.example_task.delay") as mock_delay:
           as_user.post("/api/...", data)
           mock_delay.assert_called_once_with(2, 3)
   ```

Правило: чем меньше логики в самой задаче, тем меньше нужно гонять Celery в тестах.

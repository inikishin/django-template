---
name: initial-setup
description: >-
  Первоначальная настройка нового микросервиса из этого шаблона (Django + DRF +
  PostgreSQL) и решение проблем запуска. Здесь же — выбор и подключение
  КОНФИГУРИРУЕМЫХ фич: база данных (sqlite/postgres), авторизация
  (нет/jwt/oauth/keycloak), throttling, i18n, хранение статики и медиа (сервер/s3), rich text
  (tinymce), кэш (Redis), фоновые задачи (Celery). При настройке спрашиваем
  пользователя и добавляем нужный вариант; сюда же обращаемся, чтобы переключить
  подход позже. Используй при создании проекта, переименовании, локальном запуске,
  смене БД/авторизации/хранилища, а также при ошибках запуска/импорта/подключения к БД.
  Ключевые слова: установка, настройка, запуск, venv, .env, миграции, база данных,
  sqlite, postgres, авторизация, jwt, oauth, keycloak, throttling, i18n, s3, статика,
  tinymce, кэш, Celery, setup, troubleshooting.
metadata:
  type: project-setup
  language: ru
---

# Первоначальная настройка и устранение проблем

Микросервис на Django + DRF, PostgreSQL. Код — в `src/`, ядро/настройки — пакет
`app/` (см. скил `project-structure`). Многие возможности (БД, авторизация, throttling,
i18n, хранилище статики/медиа, rich text, кэш, Celery) **конфигурируются** — по
умолчанию включён минимальный набор (см. раздел «Опциональные фичи»).

## Требования

- Python **3.12**.
- БД: по умолчанию **sqlite** (ставить ничего не нужно). PostgreSQL — если выбран вариант postgres.
- Redis — только если подключаешь кэш и/или Celery.

## Локальный запуск с нуля

```bash
# 0. Активировать скилы для Claude Code (однократно): перенести skills/ в .claude/.
#    В шаблоне скилы лежат в skills/ и не активны, пока не окажутся в .claude/skills/.
mkdir -p .claude && mv skills .claude/skills

# 1. Виртуальное окружение (именно python3.12)
python3.12 -m venv .venv

# 2. Зависимости (runtime + dev/тесты)
.venv/bin/pip install -r dev-requirements.txt

# 3. Переменные окружения
cp .env.example .env      # затем отредактировать значения

# 4. База данных: по умолчанию sqlite — создавать отдельно не нужно
#    (файл db.sqlite3 появится при migrate). Для postgres см. «Опциональные фичи».

# 5. Миграции
cd src && python manage.py migrate

# 6. Суперпользователь для админки (опционально)
cd src && python manage.py createsuperuser

# 7. Запуск
make run                          # http://localhost:8000
```

Проверка работоспособности (пути зависят от `API_PREFIX`, по умолчанию `api`):

- Swagger UI: `http://localhost:8000/api/swagger/`
- OpenAPI-схема: `http://localhost:8000/api/schema/`
- Админка: `http://localhost:8000/admin/`
- Тесты: `make test`

## Опциональные фичи (конфигурируются под проект)

При первичной настройке **ЗАДАЙ пользователю вопросы** ниже и подключи выбранные
варианты. К этому же скилу обращаемся, когда фичу нужно **переключить позже**.
Текущая база собрана по значениям «по умолчанию» (выделены **жирным**).

1. **База данных?** — **sqlite** / postgres
2. **Авторизация?** — **без авторизации** / jwt / oauth / keycloak
3. **Throttling (ограничение частоты запросов)?** — **нет** / да
4. **i18n (интернационализация)?** — **нет** / да
5. **Хранение статики и медиа?** — **сервер Django** / s3
6. **Rich text (форматированный текст)?** — **нет** / да (tinymce)
7. **Кэш?** — **нет (locmem)** / Redis
8. **Фоновые задачи (Celery)?** — **нет** / да

Каждая фича оформлена как отдельный split-settings файл и подключается только при
выборе варианта, отличного от дефолта. Пошаговое подключение каждого варианта
(зависимости, файлы настроек, env, docker-compose, тесты) — в
[references/optional-features.md](references/optional-features.md). Готовые
файлы-шаблоны — в `assets/` этого скила (`assets/auth/`, `assets/db/`, `assets/i18n/`,
`assets/storage/`, `assets/richtext/`, `assets/cache/`, `assets/celery/`).

## Конфигурация (ключевые переменные окружения)

Все переменные задаются в `.env` в корне репозитория (пример — `.env.example`).
`.env` загружается через **python-dotenv** (`load_dotenv` в `app/config/environ.py`) —
единый подход к работе с окружением во всех наших микросервисах. Типизированный
доступ (`env.bool`/`env.int`/`env.list`) даёт небольшой хелпер `env` там же.

| Переменная | Назначение | По умолчанию |
| --- | --- | --- |
| `SECRET_KEY` | секретный ключ Django | — |
| `DEBUG` | режим отладки | `0` |
| `ALLOWED_HOSTS` | разрешённые хосты (через запятую) | localhost,127.0.0.1 |
| `API_PREFIX` | префикс пути всех методов API (`api` -> `/api/...`; пусто -> в корне) | `api` |
| `PORT` | порт, который слушает сервис (`make run`, gunicorn, compose) | `8000` |
| `DB_HOST` / `DB_PORT` / `DB_NAME` / `DB_USER` / `DB_PASS` | только для варианта postgres | — |
| `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` | только если включены кэш/Celery (см. «Опциональные фичи») | — |

`API_PREFIX` важен для микросервисов: за шлюзом сервис можно смонтировать под нужным
путём, не меняя код. Менять порт: `make run PORT=9000` (или `PORT` в окружении), в
docker-compose порт берётся из `.env`.

## Запуск через docker-compose

```bash
docker compose up -d              # только сервис django (БД по умолчанию sqlite)
```

Сервисы `db` (postgres), `redis`, `celery_worker`, `celery_beat` добавляются при
подключении соответствующих вариантов/фич (см.
[references/optional-features.md](references/optional-features.md)).

## Переименование/адаптация шаблона под новый сервис

1. Перенести скилы в `.claude/`, чтобы Claude Code их подхватил: `mkdir -p .claude &&
   mv skills .claude/skills` (в шаблоне они лежат в `skills/` и до переноса не активны).
2. Изменить заголовок API в `app/config/api.py` (`SPECTACULAR_SETTINGS["TITLE"]`).
3. **Удалить пример-приложение `posts`** (это только демонстрация): убрать из
   `LOCAL_APPS` (`app/config/installed_apps.py`) и из `api_urlpatterns` в `app/urls.py`,
   удалить каталог `src/posts/`, а также пример данных `fixtures/tags.json` и тест
   `src/app/tests/test_loaddata.py` (он завязан на `posts`).
4. **`users` НЕ удаляем** — это кастомная модель пользователя (`AUTH_USER_MODEL =
   "users.User"`), ядро проекта; удаление сломает auth и админку. Если список
   пользователей не нужен в API — можно убрать только `users/api/` и `users/urls.py`
   (плюс строку с `users` из `api_urlpatterns`), оставив модель.
5. Ядро `app/` оставляем.
6. Добавлять свои приложения по скилу `project-structure`.

## Устранение типичных проблем

### venv не находит Python после обновления системы
venv привязан к конкретному минорному Python (например 3.11), которого больше нет.
Решение — пересоздать окружение:
```bash
rm -rf .venv && python3.12 -m venv .venv && .venv/bin/pip install -r dev-requirements.txt
```

### ModuleNotFoundError: No module named '<пакет>' после установки
Чаще всего venv собран под старый Python или зависимости не доустановлены —
пересоздай окружение и поставь зависимости заново (см. пункт выше). В чистом venv
Python 3.12 нет `setuptools`; если какой-то пакет требует `pkg_resources`, добавь
`setuptools` в зависимости.

### django.db.utils.OperationalError: database "<name>" does not exist
PostgreSQL запущен и доступен, но базы из `DB_NAME` нет. Создать:
```bash
createdb -U <DB_USER> <DB_NAME>
# или через psql:
psql -U postgres -c 'CREATE DATABASE <DB_NAME>;'
```
Проверить, что значения в `.env` (DB_HOST/PORT/NAME/USER/PASS) верны.

### Не подключается к Redis / падает Celery
Актуально, только если подключены кэш и/или Celery. Поднять Redis
(`docker compose up -d redis`) или указать верный `REDIS_URL` / `CELERY_BROKER_URL`
в `.env`. В тестах Redis не нужен (бандлы задают `USE_IN_MEMORY_CACHE=True` /
`CELERY_ALWAYS_EAGER=True` в `pytest.ini`).

### Тесты падают на создании тестовой БД
Пользователю БД нужно право `CREATEDB`:
```sql
ALTER USER <DB_USER> CREATEDB;
```

### Конфликт версий при pip install
`pytest-env` требует `pytest>=7.4.3`. Версии зафиксированы в
`requirements.txt` / `dev-requirements.txt` — меняя одну, проверяй совместимость.

### Изменили модель — сервер/тесты ругаются на схему БД
Создать и применить миграции: `cd src && python manage.py makemigrations && python manage.py migrate`
(см. скил `create-model`).

## Связанные скилы

- Структура и конвенции — `project-structure`.
- Модели — `create-model`; эндпоинты — `generate-api-method`; тесты — `backend-testing`.

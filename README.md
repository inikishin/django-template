# Django microservice template

## Версия: 0.1.0

Переиспользуемый шаблон API-бекенда микросервиса на Django + Django REST Framework.
Из него создаются новые сервисы с готовым ядром, конвенциями и инструментами.

## Стек и возможности

* Django 6.0 + Django REST Framework
* Документация OpenAPI на **drf-spectacular** (Swagger UI: `/api/swagger/`, схема: `/api/schema/`)
* Аутентификация — **опционально** (по умолчанию без авторизации; варианты jwt/oauth — см. скил `initial-setup`)
* Опциональные фичи (подключаются при настройке по запросу): кэш на Redis, фоновые
  задачи Celery — шаблоны в скиле `initial-setup`
* СУБД — **SQLite** по умолчанию (PostgreSQL — опциональный вариант)
* Раздельные настройки (django-split-settings) в пакете `app/config/`
* Ядро `app/`: базовые модели, вьюсеты, сериализаторы, фильтры, роутер, тестовый клиент
* Тесты — pytest + django_dynamic_fixture
* Линтер/форматтер — ruff (pre-commit)
* Docker + docker-compose (сервис django; sqlite по умолчанию)
* Пример-приложение `posts` (демонстрирует паттерны; удаляется при старте проекта)
* `users` — кастомная модель пользователя (`AUTH_USER_MODEL`), ядро проекта (не удаляем)
* Скилы для генерации кода моделями в `skills/` (активируются переносом в `.claude/`)

## Структура

Весь код — в `src/`. Ядро и настройки — пакет `app/`. Подробно — в
`skills/project-structure/`.

## Установка и запуск

```shell
python3.12 -m venv .venv
.venv/bin/pip install -r dev-requirements.txt
cp .env.example .env                # отредактировать значения
cd src && python manage.py migrate
cd src && python manage.py createsuperuser   # опционально
make run                            # http://localhost:8000
```

Через Docker:

```shell
docker compose up -d
```

Подробная настройка и решение проблем — в скиле `skills/initial-setup/`.

## Команды Makefile

| Команда | Назначение |
| --- | --- |
| `make run` | локальный сервер |
| `make test` | тесты |
| `make lint` | линтер/форматтер (ruff) |
| `make dumpdata app=<app> model=<Model>` | экспорт таблицы в json |
| `make loaddata file=<f.json>` | импорт фикстур из файла/файлов |

## Скилы для Claude Code

В `skills/` лежат скилы, описывающие конвенции проекта для генерации кода:
`project-structure`, `create-model`, `generate-api-method`, `backend-testing`,
`initial-setup`. Чтобы Claude Code их подхватил, перенесите папку в `.claude/`
(см. скил `initial-setup`). Написаны на русском (английская версия — позже).

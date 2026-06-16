---
name: project-structure
description: >-
  Карта структуры проекта-микросервиса на Django + DRF (этот шаблон): где лежат
  настройки, базовые классы, приложения, API, тесты, и каким конвенциям следовать.
  Используй ВСЕГДА перед внесением изменений в проект — чтобы класть код в нужное
  место и не нарушать стиль. Ключевые слова: структура проекта, куда положить файл,
  где настройки, новое приложение, конвенции кода, app/, api/, settings.
metadata:
  type: project-convention
  language: ru
---

# Структура проекта и конвенции

Микросервис на Django + DRF. Весь код Python лежит в каталоге `src/`.
Ядро (базовые классы и настройки) — пакет `app/`. Бизнес-логика — отдельные
Django-приложения.

## Дерево каталогов

Конфигурация уровня репозитория (env, pytest, докер, линтер) лежит в КОРНЕ, а
весь Python-код — в `src/`.

```
.                            # корень репозитория
├── .env                     # переменные окружения (НЕ коммитим; рядом .env.example)
├── pytest.ini               # конфиг pytest (pythonpath=src, testpaths=src)
├── Makefile, ruff.toml, .pre-commit-config.yaml
├── Dockerfile, docker-compose.yml
├── requirements.txt, dev-requirements.txt
├── scripts/                 # вспомогательные скрипты (entrypoint.sh и т.п.)
├── skills/                   # скилы шаблона (при настройке переносим в .claude/)
├── fixtures/                 # JSON-дампы тестовых данных (грузит фикстура load_data)
├── db.sqlite3                # БД по умолчанию (в .gitignore); staticfiles/, media/ тоже тут
└── src/                      # ТОЛЬКО python-код
    ├── manage.py
    ├── conftest.py              # тонкий: переэкспорт фикстур из app.tests.fixtures
    ├── app/                     # ЯДРО: переиспользуемые классы + настройки (тоже Django-приложение)
    │   ├── settings.py          # тонкий: SECRET_KEY, DEBUG, include(config/*)
    │   ├── urls.py              # корневой urlconf (admin, swagger, api_urlpatterns)
    │   ├── config/              # split-settings: api, auth, db, http, i18n, ... (cache/celery - опц.)
    │   ├── api/                 # переиспользуемые элементы API (наследуемся в приложениях)
    │   │   ├── viewsets.py      #   DefaultModelViewSet, ReadonlyModelViewSet, миксины
    │   │   ├── serializers.py   #   ReadOnlyModelSerializer
    │   │   ├── filtersets.py    #   SearchFilterSet
    │   │   ├── routers.py       #   DefaultRouter (DELETE на список -> bulk_delete)
    │   │   ├── pagination.py    #   StandardResultsSetPagination (page/page_size)
    │   │   └── permissions.py   #   IsAuthenticated, ReadOnly
    │   ├── models.py            # ТОЛЬКО миксины/базовые классы (DefaultModel, UUIDModel, ...); моделей нет
    │   ├── tests/               # общие тест-объекты: api.py (ApiClient), fixtures.py, loaddata.py
    │   ├── wsgi.py / asgi.py
    │   └── apps.py
    └── <приложение>/            # posts - пример (удаляем); users - кастомный User (ядро)
        ├── models.py            # модели + QuerySet/Manager (паттерн репозитория)
        ├── constants.py         # константы приложения
        ├── admin.py
        ├── apps.py
        ├── urls.py              # DefaultRouter + path()
        ├── api/                 # слой представления (HTTP); БЕЗ бизнес-логики
        │   ├── viewsets.py      #   вьюхи/вьюсеты: обработка запроса, валидация, ответ
        │   ├── serializers.py   #   сериализаторы
        │   ├── filtersets.py    #   настройки django-filter
        │   └── schema.py        #   extend_schema-дескрипторы для swagger
        ├── services/            # бизнес-логика: class-based сервисы (вызываются из вьюх/admin/CLI/задач)
        ├── tasks/               # Celery-задачи (если фича включена)
        ├── tests/               # тесты + фикстуры/фабрики
        │   ├── conftest.py      #   фикстуры/фабрики приложения (опц., только если они есть)
        │   ├── api/             #   тесты эндпоинтов
        │   └── services/        #   тесты бизнес-логики
        └── migrations/
```

## Слои приложения

Чёткое разделение ответственности:

- **`models.py`** — данные. Переиспользуемые выборки выносим в кастомные
  `QuerySet`/`Manager` (паттерн репозитория): `Post.objects.published()`.
- **`services/`** — бизнес-логика. Отдельный слой; вызывается из вьюх, экшенов
  админки, CLI-команд, Celery-задач. Оформляем как **class-based сервисы** (даже с
  одним методом) — см. скил `generate-api-method`.
- **`api/` (viewsets)** — слой HTTP. Только приём запроса, валидация (через
  сериализаторы), вызов сервиса и формирование ответа. **Никакой бизнес-логики.**
- **`constants.py`** — константы приложения (импортируем там, где нужны).

Пример: вьюсет `posts` в `@action similar` лишь вызывает `SimilarPostsService(post)()`
и отдаёт ответ; сам запрос к БД живёт в сервисе, а `published()` — в `PostQuerySet`.

## Куда что класть

| Что добавляем | Куда |
| --- | --- |
| Модель | `<app>/models.py` (см. скил create-model) |
| Бизнес-логика | `<app>/services/` (вызывается из вьюх/admin/CLI/задач) |
| Константа приложения | `<app>/constants.py` |
| Эндпоинт / ViewSet / @action | `<app>/api/viewsets.py` (тонкие; логику зовём из `services/`) (см. generate-api-method) |
| Сериализатор | `<app>/api/serializers.py` |
| Фильтр / поиск | `<app>/api/filtersets.py` (наследуем `SearchFilterSet`) |
| Описание для swagger | `<app>/api/schema.py` |
| Маршруты приложения | `<app>/urls.py`, затем добавить в список `api_urlpatterns` в `app/urls.py` |
| Тест | `<app>/tests/api/` или `<app>/tests/services/` (см. backend-testing) |
| Фикстура/фабрика приложения (если есть) | `<app>/tests/conftest.py` (создаём только при наличии своих фикстур) |
| Общая (на все приложения) фикстура | `app/tests/fixtures.py` (переэкспорт в `src/conftest.py`) |
| Настройка Django | соответствующий модуль в `app/config/` (НЕ в `settings.py`) |
| Celery-задача (если фича включена) | `<app>/tasks/` (пакет; автодискавер; см. `initial-setup`) |
| Базовый класс, общий для всех приложений | `app/...` |

## Пакет `app/` (ядро) — правила

`app/` — основное приложение с настройками сервиса и переиспользуемыми элементами.

- **`api/`** — то, что переиспользуется в других приложениях (наследуемся): пагинация,
  базовые сериализаторы/вьюхи/вьюсеты/роутер/permissions. Конкретных эндпоинтов здесь нет.
- **`config/`** — подключаемые модули настроек (split-settings); включаются в
  `include(...)` в `app/settings.py`. Меняем настройку в нужном модуле, не в `settings.py`.
- **`tests/`** — общие тест-объекты: `api.py` (`ApiClient`), `fixtures.py` (общие
  фикстуры + `__all__`), `loaddata.py` (фикстура `load_data` грузит JSON-дампы из
  `fixtures/`). Сами дампы тестовых данных — в `fixtures/*.json`.
- **`urls.py`** — один файл: корневой urlconf (admin, swagger/redoc/schema) и список
  `api_urlpatterns` с маршрутами приложений. Отдельного пакета `urls/` нет.
- **`models.py`** — ТОЛЬКО миксины и базовые классы для наследования
  (`DefaultModel`, `UUIDModel`, `TimeStampedMixin`, `IsActiveMixin`, `MoneyField`).
  Конкретные модели в `app/` не создаются.

## Базовые классы (всегда наследуемся от них)

- Модели: `app.models.DefaultModel` / `UUIDModel` (+ миксины `TimeStampedMixin`, `IsActiveMixin`).
- ViewSet: `app.api.viewsets.DefaultModelViewSet` (CRUD) / `ReadonlyModelViewSet` (чтение).
- FilterSet: `app.api.filtersets.SearchFilterSet`.
- Router: `app.api.routers.DefaultRouter`.
- В тестах: `app.tests.ApiClient`; загрузка дампов — фикстура `load_data` (см. backend-testing).

## Новое приложение

1. `cd src && python manage.py startapp <name>`, затем привести к структуре выше:
   создать `api/` (`viewsets.py`/`serializers.py`/`filtersets.py`/`schema.py`), `tests/`
   и, по мере необходимости, `services/`, `constants.py`, `tasks/`.
2. Добавить `"<name>"` в `LOCAL_APPS` в `app/config/installed_apps.py`.
3. Подключить `path("<name>/", include("<name>.urls"))` в `app/urls.py`.

## Конвенции кода (из эталонного проекта)

Подробный свод правил — в [references/conventions.md](references/conventions.md). Кратко:

- Форматирование: ruff (аналог black), длина строки **120**, кавычки **двойные**.
- Импорты: isort, 3 блока (stdlib / сторонние / локальные); точечный импорт сущностей,
  модули stdlib — целиком; `import *` запрещён.
- Многострочные перечисления — с запятой после последнего элемента.
- В `__init__.py` — только импорты.
- `verbose_name` и текст для пользователя — на русском через `gettext_lazy as _`.
- Логи — на английском.
- Докстринг в одну строку заканчивается точкой.
- Фильтры и выборки выносим в кастомные QuerySet/Manager (паттерн «репозиторий»).
- Удаляем мёртвый/закомментированный код; TODO/FIXME не оставляем в коммите.

## Связанные скилы

- Модели — `create-model`.
- Эндпоинты — `generate-api-method`.
- Тесты — `backend-testing`.
- Настройка/запуск/проблемы — `initial-setup`.

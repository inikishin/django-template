---
name: backend-testing
description: >-
  Написание и отладка тестов микросервиса на Django + DRF (pytest +
  django_dynamic_fixture + ApiClient). Что тестируем (все API-методы:
  запрос/ответ/валидация; сервисы; queryset/manager; задачи), структура тестов по
  приложениям, фикстуры, тестовые данные (G() для простых кейсов, дампы fixtures/ +
  load_data для сложных), целевое покрытие (≥70%, pytest-cov, make cov). Используй при
  создании тестов API/сервисов/моделей или разборе падающих тестов. Ключевые слова:
  тест, pytest, фикстура, G(), ApiClient, as_user, сервис, queryset, coverage,
  покрытие, дамп, django_db, упал тест.
metadata:
  type: project-convention
  language: ru
---

# Тестирование бэкенда

Стек: `pytest` + `pytest-django` + `django_dynamic_fixture` (фабрика `G`) + `ApiClient`.
Источник правды — `pytest.ini`, `src/conftest.py`, `src/app/tests/`. Структура проекта —
скил `project-structure`.

## Что тестируем (минимум)

- **Все API-методы** — статус ответа, тело ответа и валидацию: happy path **плюс**
  негативный сценарий (400/401/403/404 и т.п.).
- **Сервисы** (`<app>/services/`) — и сложную, и простую логику.
- **Кастомные QuerySet/Manager** (паттерн репозитория, напр. `published()`).
- **Celery-задачи** — если фича включена (см. раздел в `initial-setup`).
- Покрытие — **не ниже 70%** (см. ниже).

## Где лежат тесты

- `<app>/tests/api/` — тесты эндпоинтов.
- `<app>/tests/services/` — тесты сервисов.
- `<app>/tests/test_models.py` — модели и кастомные QuerySet/Manager.
- Имена файлов: `test*.py`. Каждый каталог тестов — с пустым `__init__.py`.
- **Общие** фикстуры (на все приложения) — в `app/tests/fixtures.py` (переэкспорт в
  `src/conftest.py`). **Фикстуры приложения** — в `<app>/tests/conftest.py` (создаём
  только если они есть; в каждом приложении не нужен).

## Фикстуры (из `app/tests/fixtures.py`)

| Фикстура | Что даёт |
| --- | --- |
| `user` / `admin_user` | пользователь / суперпользователь |
| `as_user` / `as_admin` | `ApiClient`, аутентифицированный соответствующим пользователем |
| `api_client` | анонимный `ApiClient` |
| `load_data` | грузит JSON-дампы из `fixtures/*.json` в тестовую БД |

## Тестовые данные: `G()` vs дампы

- **`G()` (django_dynamic_fixture)** — для **простых CRUD-подобных** кейсов: автозаполняет
  обязательные поля и связи прямо в тесте.
  ```python
  post = G(Post, is_draft=False)     # один объект
  posts = G(Post, n=3)               # список
  post = G(Post, tags=[G(Tag)])      # M2M через список
  ```
- **Дампы (`fixtures/*.json` + фикстура `load_data`)** — для **новых и сложных кейсов с
  данными**: справочники, связанные графы объектов, граничные значения. Добавляем дамп,
  подключаем `load_data` в тест:
  ```python
  @pytest.mark.django_db
  def test_smth(load_data, as_user):
      ...  # данные из fixtures/ уже в БД
  ```
  Файлы грузятся по алфавиту; порядок по FK — префиксом имени (`01_users.json`).
  Создать дамп: `make dumpdata app=<app> model=<Model>`. **Принцип:** каждая строка
  дампа оправдана конкретным тестом; не зеркалим прод-базу.

## ApiClient

`app.tests.ApiClient` (обёртка над DRF APIClient): сам проверяет статус и возвращает
распарсенный JSON. Ожидаемый статус по умолчанию: get=200, post=201, patch/put=200,
delete=204; переопределяется через `expected_status`. `as_response=True` — «сырой»
Response. Тело и ответ — обычный JSON DRF (поля в `snake_case`).

## Тесты API (`tests/api/`)

```python
import pytest
from django_dynamic_fixture import G

from posts.models import Post


@pytest.mark.django_db
class TestPostViewSet:
    def test_list_returns_only_published(self, as_user):
        G(Post, is_draft=False)
        G(Post, is_draft=True)

        result = as_user.get("/api/posts/")

        assert result["count"] == 1

    def test_create(self, as_user, user):
        data = {"title": "Title", "content": "Body", "author": user.pk, "is_draft": False}

        result = as_user.post("/api/posts/", data)

        assert Post.objects.count() == 1
        assert result["slug"]  # заполнен автоматически (calculate_slug)

    def test_create_validation_error(self, as_user):
        # негативный сценарий: нет обязательных полей -> 400
        as_user.post("/api/posts/", {}, expected_status=400)
```

Проверяем и статус, и тело; для каждого публичного метода — минимум happy path +
негатив.

## Тесты сервисов (`tests/services/`)

Сервис — class-based (см. `generate-api-method`). Обычно тестируем «через данные»:
готовим данные (`G()` или `load_data`), вызываем сервис, проверяем результат.

```python
import pytest
from django_dynamic_fixture import G

from posts.models import Post, Tag
from posts.services.post import SimilarPostsService


@pytest.mark.django_db
class TestSimilarPostsService:
    def test_returns_published_posts_with_shared_tags(self):
        tag = G(Tag)
        post = G(Post, is_draft=False, tags=[tag])
        similar = G(Post, is_draft=False, tags=[tag])
        G(Post, is_draft=False)  # без общих тегов -> не попадает

        result = SimilarPostsService(post)()

        assert set(result) == {similar}

    def test_excludes_drafts(self):
        tag = G(Tag)
        post = G(Post, is_draft=False, tags=[tag])
        G(Post, is_draft=True, tags=[tag])

        assert list(SimilarPostsService(post)()) == []
```

Если сервис оркестрирует **внешние вызовы** (другой сервис, HTTP-клиент, Celery-задачу) —
эти зависимости мокаем (`unittest.mock`), проверяя, что они вызваны с нужными
аргументами, а не дёргаем их по-настоящему.

## Тесты QuerySet/Manager (`tests/test_models.py`)

```python
@pytest.mark.django_db
class TestPostQuerySet:
    def test_published_excludes_drafts(self):
        G(Post, is_draft=False)
        G(Post, is_draft=True)

        assert Post.objects.published().count() == 1
```

## Запуск и покрытие

Запускаем из КОРНЯ репозитория (`pytest.ini`: `pythonpath=src`, `testpaths=src`):

```bash
make test                                   # быстрый прогон
make cov                                    # с покрытием: term-missing + htmlcov/ + порог 70%
pytest src/posts/tests/services/test_post.py::TestSimilarPostsService  # один класс
pytest -k similar                           # по подстроке имени
```

**Покрытие.** Цель — **≥70%** (строки), задано в `.coveragerc` (`fail_under = 70`).
`make cov` (использует `pytest-cov`) печатает непокрытые строки и пишет HTML-отчёт в
`htmlcov/index.html`; при покрытии ниже 70% команда падает. Для нового кода — тот же
порог; выше — приветствуется. По умолчанию БД в тестах — sqlite (in-memory), внешняя
БД не нужна.

## Типичные причины падений

- **400 на запись** — неверные имена полей (`snake_case`, как в модели) или не переданы
  обязательные поля.
- **401 при включённой авторизации** — взят `api_client` (аноним) вместо `as_user`
  (в базе без авторизации оба дают одинаковый доступ).
- **Объект не создаётся через `G()`** — обязательное поле без подходящего значения;
  задайте явно `G(Model, field=...)`.
- **Неожиданный slug/значение** — поле заполняется хуком `calculate_*` на save();
  проверяйте итог после сохранения.
- **`coverage` ниже 70%** — добавьте тесты на непокрытые ветки (см. `make cov`
  term-missing) либо обоснуйте в PR.
- **Тест падает только вместе с другими** — тесты не изолированы; не полагайтесь на
  порядок, готовьте данные в самом тесте/фикстуре.

---
name: backend-testing
description: >-
  Writing and debugging tests for a Django + DRF microservice (pytest +
  django_dynamic_fixture + ApiClient). What to test (all API methods:
  request/response/validation; services; queryset/manager; tasks), test structure by
  app, fixtures, test data (G() for simple cases, fixtures/ dumps +
  load_data for complex ones), target coverage (≥70%, pytest-cov, make cov). Use when
  creating API/service/model tests or investigating failing tests. Keywords:
  test, pytest, fixture, G(), ApiClient, as_user, service, queryset, coverage,
  fixture dump, django_db, failing test.
metadata:
  type: project-convention
  language: en
---

# Backend testing

Stack: `pytest` + `pytest-django` + `django_dynamic_fixture` (the `G` factory) + `ApiClient`.
Source of truth — `pytest.ini`, `src/conftest.py`, `src/app/tests/`. Project structure —
the `project-structure` skill.

## What to test (minimum)

- **All API methods** — response status, response body and validation: happy path **plus**
  a negative case (400/401/403/404 etc.).
- **Services** (`<app>/services/`) — both complex and simple logic.
- **Custom QuerySet/Manager** (repository pattern, e.g. `published()`).
- **Celery tasks** — if the feature is enabled (see the section in `initial-setup`).
- Coverage — **no lower than 70%** (see below).

## Where tests live

- `<app>/tests/api/` — endpoint tests.
- `<app>/tests/services/` — service tests.
- `<app>/tests/test_models.py` — models and custom QuerySet/Manager.
- File names: `test*.py`. Each test directory has an empty `__init__.py`.
- **Shared** fixtures (for all apps) — in `app/tests/fixtures.py` (re-exported in
  `src/conftest.py`). **App fixtures** — in `<app>/tests/conftest.py` (created
  only if they exist; not required in every app).

## Fixtures (from `app/tests/fixtures.py`)

| Fixture | What it provides |
| --- | --- |
| `user` / `admin_user` | a user / a superuser |
| `as_user` / `as_admin` | an `ApiClient` authenticated as the corresponding user |
| `api_client` | an anonymous `ApiClient` |
| `load_data` | loads JSON dumps from `fixtures/*.json` into the test DB |

## Test data: `G()` vs dumps

- **`G()` (django_dynamic_fixture)** — for **simple CRUD-like** cases: auto-fills
  required fields and relations right in the test.
  ```python
  post = G(Post, is_draft=False)     # a single object
  posts = G(Post, n=3)               # a list
  post = G(Post, tags=[G(Tag)])      # M2M via a list
  ```
- **Dumps (`fixtures/*.json` + the `load_data` fixture)** — for **new and complex
  data-heavy cases**: lookup tables, related object graphs, boundary values. Add a dump,
  wire `load_data` into the test:
  ```python
  @pytest.mark.django_db
  def test_smth(load_data, as_user):
      ...  # data from fixtures/ is already in the DB
  ```
  Files load alphabetically; FK ordering is controlled by a name prefix (`01_users.json`).
  Create a dump: `make dumpdata app=<app> model=<Model>`. **Principle:** every line in
  the dump is justified by a concrete test; do not mirror the prod database.

## ApiClient

`app.tests.ApiClient` (a wrapper over DRF APIClient): it checks the status itself and returns
the parsed JSON. Default expected status: get=200, post=201, patch/put=200,
delete=204; overridden via `expected_status`. `as_response=True` — the raw
Response. Body and response are plain DRF JSON (fields in `snake_case`).

## API tests (`tests/api/`)

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
        assert result["slug"]  # filled in automatically (calculate_slug)

    def test_create_validation_error(self, as_user):
        # negative case: required fields missing -> 400
        as_user.post("/api/posts/", {}, expected_status=400)
```

Check both the status and the body; for every public method — at minimum a happy path +
a negative case.

## Service tests (`tests/services/`)

A service is class-based (see `generate-api-method`). Usually we test "through data":
prepare data (`G()` or `load_data`), call the service, check the result.

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
        G(Post, is_draft=False)  # no shared tags -> excluded

        result = SimilarPostsService(post)()

        assert set(result) == {similar}

    def test_excludes_drafts(self):
        tag = G(Tag)
        post = G(Post, is_draft=False, tags=[tag])
        G(Post, is_draft=True, tags=[tag])

        assert list(SimilarPostsService(post)()) == []
```

If a service orchestrates **external calls** (another service, an HTTP client, a Celery task) —
mock those dependencies (`unittest.mock`), asserting that they were called with the right
arguments instead of invoking them for real.

## QuerySet/Manager tests (`tests/test_models.py`)

```python
@pytest.mark.django_db
class TestPostQuerySet:
    def test_published_excludes_drafts(self):
        G(Post, is_draft=False)
        G(Post, is_draft=True)

        assert Post.objects.published().count() == 1
```

## Running and coverage

Run from the ROOT of the repository (`pytest.ini`: `pythonpath=src`, `testpaths=src`):

```bash
make test                                   # quick run
make cov                                    # with coverage: term-missing + htmlcov/ + 70% threshold
pytest src/posts/tests/services/test_post.py::TestSimilarPostsService  # a single class
pytest -k similar                           # by name substring
```

**Coverage.** Target — **≥70%** (lines), set in `.coveragerc` (`fail_under = 70`).
`make cov` (uses `pytest-cov`) prints uncovered lines and writes an HTML report to
`htmlcov/index.html`; if coverage is below 70% the command fails. For new code — the same
threshold; higher is welcome. By default the test DB is sqlite (in-memory), no external
DB is needed.

## Common causes of failures

- **400 on write** — wrong field names (`snake_case`, as in the model) or required
  fields not passed.
- **401 with authorization enabled** — `api_client` (anonymous) was used instead of `as_user`
  (in the base without authorization both give the same access).
- **Object is not created via `G()`** — a required field has no suitable value;
  set it explicitly with `G(Model, field=...)`.
- **Unexpected slug/value** — the field is filled by a `calculate_*` hook on save();
  check the result after saving.
- **`coverage` below 70%** — add tests for the uncovered branches (see `make cov`
  term-missing) or justify it in the PR.
- **A test fails only together with others** — tests are not isolated; do not rely on
  ordering, prepare data in the test/fixture itself.

---
name: initial-setup
description: >-
  Initial setup of a new microservice from this template (Django + DRF +
  PostgreSQL) and solving startup problems. Also covers choosing and wiring in
  CONFIGURABLE features: database (sqlite/postgres), authentication
  (none/jwt/oauth/keycloak), throttling, i18n, static and media storage (server/s3), rich text
  (tinymce), cache (Redis), background tasks (Celery). During setup we ask the
  user and add the chosen variant; come back here to switch the approach later.
  Use when creating a project, renaming, running locally, switching
  DB/authentication/storage, and on startup/import/DB-connection errors.
  Keywords: install, setup, run, venv, .env, migrations, database,
  sqlite, postgres, authentication, jwt, oauth, keycloak, throttling, i18n, s3, static,
  tinymce, cache, Celery, setup, troubleshooting.
metadata:
  type: project-setup
  language: en
---

# Initial setup and troubleshooting

A Django + DRF microservice, PostgreSQL. Code lives in `src/`, the core/settings are the
`app/` package (see the `project-structure` skill). Many capabilities (DB, authentication, throttling,
i18n, static/media storage, rich text, cache, Celery) are **configurable** — by
default a minimal set is enabled (see the "Optional features" section).

## Requirements

- Python **3.12**.
- DB: by default **sqlite** (nothing to install). PostgreSQL — if the postgres variant is chosen.
- Redis — only if you enable the cache and/or Celery.

## Running locally from scratch

```bash
# 0. Activate skills for Claude Code (one time): move skills/ into .claude/.
#    In the template the skills live in skills/ and are inactive until they land in .claude/skills/.
mkdir -p .claude && mv skills .claude/skills

# 1. Virtual environment (specifically python3.12)
python3.12 -m venv .venv

# 2. Dependencies (runtime + dev/tests)
.venv/bin/pip install -r dev-requirements.txt

# 3. Environment variables
cp .env.example .env      # then edit the values

# 4. Database: sqlite by default — no need to create it separately
#    (the db.sqlite3 file appears on migrate). For postgres see "Optional features".

# 5. Migrations
cd src && python manage.py migrate

# 6. Superuser for the admin (optional)
cd src && python manage.py createsuperuser

# 7. Run
make run                          # http://localhost:8000
```

Health check (paths depend on `API_PREFIX`, default `api`):

- Swagger UI: `http://localhost:8000/api/swagger/`
- OpenAPI schema: `http://localhost:8000/api/schema/`
- Admin: `http://localhost:8000/admin/`
- Tests: `make test`

## Optional features (configured per project)

During initial setup **ASK the user the questions** below and wire in the chosen
variants. Come back to this same skill when a feature needs to be **switched later**.
The current base is assembled with the "default" values (shown in **bold**).

1. **Database?** — **sqlite** / postgres
2. **Authentication?** — **no authentication** / jwt / oauth / keycloak
3. **Throttling (request rate limiting)?** — **no** / yes
4. **i18n (internationalization)?** — **no** / yes
5. **Static and media storage?** — **Django server** / s3
6. **Rich text?** — **no** / yes (tinymce)
7. **Cache?** — **no (locmem)** / Redis
8. **Background tasks (Celery)?** — **no** / yes

Each feature is laid out as a separate split-settings file and is wired in only when
a variant other than the default is chosen. Step-by-step wiring for each variant
(dependencies, settings files, env, docker-compose, tests) is in
[references/optional-features.md](references/optional-features.md). Ready-made
template files are in `assets/` of this skill (`assets/auth/`, `assets/db/`, `assets/i18n/`,
`assets/storage/`, `assets/richtext/`, `assets/cache/`, `assets/celery/`).

## Configuration (key environment variables)

All variables are set in `.env` at the repo root (example — `.env.example`).
`.env` is loaded via **python-dotenv** (`load_dotenv` in `app/config/environ.py`) —
a single approach to environment handling across all our microservices. Typed
access (`env.bool`/`env.int`/`env.list`) is provided by a small `env` helper there too.

| Variable | Purpose | Default |
| --- | --- | --- |
| `SECRET_KEY` | Django secret key | — |
| `DEBUG` | debug mode | `0` |
| `ALLOWED_HOSTS` | allowed hosts (comma-separated) | localhost,127.0.0.1 |
| `API_PREFIX` | path prefix for all API methods (`api` -> `/api/...`; empty -> at the root) | `api` |
| `PORT` | the port the service listens on (`make run`, gunicorn, compose) | `8000` |
| `DB_HOST` / `DB_PORT` / `DB_NAME` / `DB_USER` / `DB_PASS` | only for the postgres variant | — |
| `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` | only if cache/Celery are enabled (see "Optional features") | — |

`API_PREFIX` matters for microservices: behind a gateway the service can be mounted under
the desired path without changing code. Change the port: `make run PORT=9000` (or `PORT` in the
environment); in docker-compose the port is taken from `.env`.

## Running via docker-compose

```bash
docker compose up -d              # only the django service (DB defaults to sqlite)
```

The `db` (postgres), `redis`, `celery_worker`, `celery_beat` services are added when
the corresponding variants/features are wired in (see
[references/optional-features.md](references/optional-features.md)).

## Renaming/adapting the template for a new service

1. Move the skills into `.claude/` so Claude Code picks them up: `mkdir -p .claude &&
   mv skills .claude/skills` (in the template they live in `skills/` and are inactive until moved).
2. Change the API title in `app/config/api.py` (`SPECTACULAR_SETTINGS["TITLE"]`).
3. **Remove the example app `posts`** (it's only a demonstration): remove it from
   `LOCAL_APPS` (`app/config/installed_apps.py`) and from `api_urlpatterns` in `app/urls.py`,
   delete the `src/posts/` directory, as well as the example data `fixtures/tags.json` and the test
   `src/app/tests/test_loaddata.py` (it depends on `posts`).
4. **Do NOT remove `users`** — it is the custom user model (`AUTH_USER_MODEL =
   "users.User"`), the core of the project; removing it will break auth and the admin. If the user
   list is not needed in the API, you can remove only `users/api/` and `users/urls.py`
   (plus the `users` line from `api_urlpatterns`), keeping the model.
5. Keep the `app/` core.
6. Add your own apps following the `project-structure` skill.

## Troubleshooting common problems

### venv can't find Python after a system upgrade
The venv is tied to a specific minor Python (e.g. 3.11) that no longer exists.
The fix is to recreate the environment:
```bash
rm -rf .venv && python3.12 -m venv .venv && .venv/bin/pip install -r dev-requirements.txt
```

### ModuleNotFoundError: No module named '<package>' after installation
Most often the venv was built for an old Python or the dependencies weren't fully installed —
recreate the environment and reinstall the dependencies (see the item above). A clean venv on
Python 3.12 has no `setuptools`; if some package requires `pkg_resources`, add
`setuptools` to the dependencies.

### django.db.utils.OperationalError: database "<name>" does not exist
PostgreSQL is running and reachable, but the database from `DB_NAME` doesn't exist. Create it:
```bash
createdb -U <DB_USER> <DB_NAME>
# or via psql:
psql -U postgres -c 'CREATE DATABASE <DB_NAME>;'
```
Check that the values in `.env` (DB_HOST/PORT/NAME/USER/PASS) are correct.

### Can't connect to Redis / Celery crashes
Relevant only if the cache and/or Celery are enabled. Start Redis
(`docker compose up -d redis`) or set the correct `REDIS_URL` / `CELERY_BROKER_URL`
in `.env`. Tests don't need Redis (the bundles set `USE_IN_MEMORY_CACHE=True` /
`CELERY_ALWAYS_EAGER=True` in `pytest.ini`).

### Tests fail when creating the test DB
The DB user needs the `CREATEDB` privilege:
```sql
ALTER USER <DB_USER> CREATEDB;
```

### Version conflict on pip install
`pytest-env` requires `pytest>=7.4.3`. Versions are pinned in
`requirements.txt` / `dev-requirements.txt` — when changing one, check compatibility.

### Changed a model — the server/tests complain about the DB schema
Create and apply migrations: `cd src && python manage.py makemigrations && python manage.py migrate`
(see the `create-model` skill).

## Related skills

- Structure and conventions — `project-structure`.
- Models — `create-model`; endpoints — `generate-api-method`; tests — `backend-testing`.

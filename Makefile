.PHONY: install run lint test cov dumpdata loaddata check

# Port the dev server listens on. Override: `make run PORT=9000` or export PORT.
PORT ?= 8000

install:
	.venv/bin/pip install -r dev-requirements.txt

run:
	cd src && python manage.py runserver 0.0.0.0:$(PORT)

lint:
	pre-commit run --all-files

test:
	pytest --disable-warnings

# Tests with coverage (fails under 70%; HTML report in htmlcov/).
cov:
	pytest --cov --cov-report=term-missing --cov-report=html --disable-warnings

# Export a table to json: make dumpdata app=posts model=Post
dumpdata:
	cd src && python manage.py dumpdata $(app).$(model) --indent 2 -o $(model).json

# Import fixture(s) from file(s): make loaddata file=data.json (или несколько: file="a.json b.json")
loaddata:
	cd src && python manage.py loaddata $(file)

# Fail if there are model changes without a migration.
check:
	cd src && python manage.py makemigrations --check --dry-run

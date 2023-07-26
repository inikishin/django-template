run:
	cd src && python manage.py runserver

lint:
	pre-commit run --all-files

test:
	cd src && pytest

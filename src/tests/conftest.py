from pathlib import Path

import pytest
from django.core.management import call_command
from rest_framework.test import APIClient


@pytest.fixture
@pytest.mark.django_db
def loaddata():
    dir_ = Path(__file__).resolve().parent
    files = list(dir_.joinpath("data").glob("*.json"))
    for file in files:
        call_command("loaddata", file, verbosity=0)


@pytest.fixture
def api_client():
    client = APIClient()
    yield client


@pytest.fixture
@pytest.mark.django_db
def as_admin(api_client):
    url = "auth/login"
    user, password = "admin", "admin"
    response = api_client.post(url, data={"username": user, "password": password})

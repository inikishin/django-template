import pytest
from rest_framework import status


@pytest.mark.django_db
def test_login(loaddata, api_client):
    url = "/auth/login/"
    data = {"username": "admin", "password": "admin"}
    response = api_client.post(url, data=data)

    assert response.status_code == status.HTTP_200_OK

    content = response.data
    assert "access" in content
    assert "refresh" in content


@pytest.mark.django_db
def test_refresh(loaddata, api_client):
    url = "/auth/login/"
    data = {"username": "admin", "password": "admin"}
    response = api_client.post(url, data=data)
    assert response.status_code == status.HTTP_200_OK
    refresh_token = response.data.get("refresh")

    url = "/auth/refresh/"
    data = {
        "refresh": refresh_token,
    }
    response = api_client.post(url, data=data)
    assert response.status_code == status.HTTP_200_OK
    content = response.data
    assert "access" in content

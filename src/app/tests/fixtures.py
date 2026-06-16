import pytest
from django_dynamic_fixture import G

from app.tests.api import ApiClient
from app.tests.loaddata import load_data
from users.models import User

__all__ = [
    "api_client",
    "user",
    "admin_user",
    "as_user",
    "as_admin",
    "load_data",
]


@pytest.fixture
def api_client() -> ApiClient:
    """Anonymous API client."""
    return ApiClient()


@pytest.fixture
def user(db) -> User:
    """A regular authenticated user."""
    return G(User, is_active=True, is_superuser=False)


@pytest.fixture
def admin_user(db) -> User:
    """Superuser."""
    return G(User, is_active=True, is_superuser=True, is_staff=True)


@pytest.fixture
def as_user(user) -> ApiClient:
    """API client authenticated as a regular user."""
    return ApiClient(user=user)


@pytest.fixture
def as_admin(admin_user) -> ApiClient:
    """API client authenticated as a superuser."""
    return ApiClient(user=admin_user)

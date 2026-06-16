import pytest

from posts.models import Tag


@pytest.mark.django_db
def test_load_data_loads_fixtures(load_data):
    """The `load_data` fixture loads JSON dumps from src/fixtures/ into the test DB."""
    assert Tag.objects.count() == 2

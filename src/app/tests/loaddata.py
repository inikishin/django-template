import pytest
from django.core.management import call_command

from app.config.environ import PROJECT_ROOT

# Directory with JSON dumps loaded into the test DB by the `load_data` fixture.
FIXTURES_DIR = PROJECT_ROOT / "fixtures"


def load_fixtures() -> None:
    """Load all JSON dumps from src/fixtures/ (sorted; prefix names to control order)."""
    if not FIXTURES_DIR.exists():
        return
    files = sorted(FIXTURES_DIR.glob("*.json"))
    if files:
        call_command("loaddata", *[str(f) for f in files], verbosity=0)


@pytest.fixture
def load_data(db) -> None:
    """Populate the test DB from JSON dumps in src/fixtures/."""
    load_fixtures()

import os
from pathlib import Path

from dotenv import load_dotenv

# BASE_DIR points to the `src` directory (two levels above this file),
# PROJECT_ROOT - the repository root (one level above src).
BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = BASE_DIR.parent

# Load environment variables from the .env file in the repository root, if present.
# python-dotenv is the env loader used across our microservices.
load_dotenv(PROJECT_ROOT / ".env")

_UNSET = object()
_TRUE_VALUES = {"1", "true", "yes", "on", "y", "t"}


class Env:
    """Minimal typed reader over os.environ (.env is loaded via python-dotenv)."""

    def __call__(self, key, default=_UNSET):
        value = os.environ.get(key, default)
        if value is _UNSET:
            raise RuntimeError(f"Required environment variable is not set: {key}")
        return value

    def bool(self, key, default=_UNSET) -> bool:
        value = self(key, default)
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in _TRUE_VALUES

    def int(self, key, default=_UNSET) -> int:
        return int(self(key, default))

    def list(self, key, default=_UNSET, separator: str = ",") -> list[str]:
        value = self(key, default)
        if isinstance(value, list):
            return value
        if not value:
            return []
        return [item.strip() for item in value.split(separator) if item.strip()]


env = Env()

# Common fixtures are defined in app.tests.fixtures. They are re-exported here
# so that pytest picks them up for all apps (a conftest at the src/ level is visible to all tests).
from app.tests.fixtures import *  # noqa: F401,F403

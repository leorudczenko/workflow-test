import pytest
from app.main import HelloWorld


@pytest.fixture(scope="function")
def hello_world():
    hello_world_application = HelloWorld([], testing_mode=True)
    yield hello_world_application
    del hello_world_application

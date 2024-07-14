import pytest
from mockito import unstub, verifyStubbedInvocationsAreUsed


@pytest.fixture(autouse=True)
def ensure_all_mocks_were_called():
    yield
    try:
        verifyStubbedInvocationsAreUsed()
    finally:
        unstub()

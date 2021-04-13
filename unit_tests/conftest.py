import pytest
from pytest_socket import disable_socket
from wagtail.core.models import Locale


def pytest_runtest_setup():
    disable_socket()


@pytest.fixture
def default_locale(db):
    return Locale.objects.create(language_code='en')

import pytest

from crm.gmail_utils import get_raw_messages


@pytest.fixture
def gmail_service(mock, gmail_api_response_factory):
    service = mock.Mock()
    mock.patch('crm.gmail_utils.get_labels', lambda s: gmail_api_response_factory("gmapi_labels_response.json"))
    return service


def test_get_raw_messages(gmail_service):
    get_raw_messages(gmail_service)

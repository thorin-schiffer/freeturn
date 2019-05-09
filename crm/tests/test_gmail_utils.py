import pytest

from crm.gmail_utils import get_raw_messages


@pytest.fixture
def gmail_service(mock, gmail_api_response_factory):
    service = mock.Mock()
    mock.patch('crm.gmail_utils.get_labels', lambda s: gmail_api_response_factory("gmapi_labels_response.json"))
    mock.patch('crm.gmail_utils.get_messages',
               lambda s, l: {"messages": [gmail_api_response_factory("gmail_api_message.json")]})
    return service


def test_get_raw_messages(gmail_service):
    result = get_raw_messages(gmail_service)
    assert len(result) == 1

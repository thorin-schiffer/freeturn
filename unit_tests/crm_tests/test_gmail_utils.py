import pytest

from crm.gmail_utils import get_raw_messages, sync
from crm.models import ProjectMessage
from crm.utils import Credentials


@pytest.fixture
def gmail_service(mocker, gmail_api_response_factory):
    service = mocker.Mock()
    mocker.patch('crm.gmail_utils.get_labels', lambda s: gmail_api_response_factory("gmapi_labels_response.json"))
    mocker.patch('crm.gmail_utils.get_message_ids',
                 lambda s, l: {"messages": [gmail_api_response_factory("gmail_api_message.json")]})
    mocker.patch('crm.gmail_utils.get_message_raws',
                 lambda s, l: gmail_api_response_factory("gmail_api_message.json"))
    return service


def test_get_raw_messages(gmail_service):
    result = get_raw_messages(gmail_service)
    assert len(result) == 1


@pytest.mark.django_db
def test_sync(gmail_service, user_social_auth):
    sync()
    message = ProjectMessage.objects.first()
    assert message.project
    assert message.author
    assert message.sent_at
    assert message.author
    assert message.text
    assert message.gmail_message_id
    assert message.gmail_thread_id


@pytest.mark.django_db
def test_creds_refresh(gmail_service, user_social_auth, mocker):
    creds = Credentials(user_social_auth)

    def fake_refresh_token(*args, **kwargs):
        user_social_auth.extra_data["refresh_token"] = "x"

    mocker.patch("social_django.models.UserSocialAuth.refresh_token",
                 side_effect=fake_refresh_token)
    creds.refresh(mocker.Mock())
    assert creds._refresh_token == "x"

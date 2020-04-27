import pytest

from crm import gmail_utils
from crm.models import ProjectMessage
from crm.utils import Credentials


@pytest.fixture
def gmail_service(mocker, gmail_api_response_factory, monkeypatch, settings):
    monkeypatch.setenv("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY", "111")
    monkeypatch.setenv("SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET", "111")
    settings.AUTHENTICATION_BACKENDS = (
        'social_core.backends.google.GoogleOAuth2',
        'django.contrib.auth.backends.ModelBackend',
    )
    service = mocker.Mock()
    mocker.patch('googleapiclient.discovery.build', return_value=service)
    mocker.patch('crm.gmail_utils.get_labels', lambda s: gmail_api_response_factory("gmapi_labels_response.json"))
    mocker.patch('crm.gmail_utils.get_message_ids',
                 lambda s, l: {"messages": [gmail_api_response_factory("gmail_api_message.json")]})
    mocker.patch('crm.gmail_utils.get_message_raws',
                 lambda s, l: gmail_api_response_factory("gmail_api_message.json"))
    return service


def test_get_raw_messages(gmail_service):
    result = gmail_utils.get_raw_messages(gmail_service)
    assert len(result) == 1


@pytest.mark.django_db
def test_sync(gmail_service, user_social_auth):
    gmail_utils.sync()
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

import pytest

from crm import gmail_utils
from crm.factories import UserSocialAuthFactory
from crm.models.project_message import ProjectMessage
from crm.utils import Credentials


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
        user_social_auth.extra_data['refresh_token'] = 'x'

    mocker.patch('social_django.models.UserSocialAuth.refresh_token',
                 side_effect=fake_refresh_token)
    creds.refresh(mocker.Mock())
    assert creds._refresh_token == 'x'


@pytest.mark.django_db
def test_multiple_social_auths(gmail_service):
    # https://sentry.io/organizations/thorin-schiffer/issues/2474133927/?project=1304745&query=is%3Aunresolved
    first_auth = UserSocialAuthFactory()
    UserSocialAuthFactory(user=first_auth.user)
    gmail_utils.sync()
    assert ProjectMessage.objects.count() == 1  # because user is the same

import base64
import email
from io import BytesIO

import pytest

from crm import gmail_utils
from crm.factories import UserSocialAuthFactory
from crm.gmail_utils import send_email, create_message_with_attachment
from crm.models import CV
from crm.models.project_message import ProjectMessage
from crm.utils import Credentials


def test_get_raw_messages(gmail_service):
    result = gmail_utils.get_raw_messages(gmail_service)
    assert len(result) == 1


@pytest.mark.django_db
def test_sync(gmail_service, user_social_auth, default_site):
    gmail_utils.sync()
    message = ProjectMessage.objects.first()
    assert message.project
    assert message.author
    assert message.sent_at
    assert message.author
    assert message.text
    assert message.gmail_message_id
    assert message.gmail_thread_id
    assert CV.objects.filter(project=message.project).exists()


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
def test_multiple_social_auths(default_site, gmail_service):
    # https://sentry.io/organizations/thorin-schiffer/issues/2474133927/?project=1304745&query=is%3Aunresolved
    first_auth = UserSocialAuthFactory()
    UserSocialAuthFactory(user=first_auth.user)
    gmail_utils.sync()
    assert ProjectMessage.objects.count() == 1  # because user is the same


def test_create_message_with_pdf_attachment(faker):
    sender = faker.email()
    to = faker.email()
    message = create_message_with_attachment(
        sender=sender,
        to=to,
        message_text_html='<p>test <b>test</b></p>',
        file=BytesIO(b'test'),
        content_type='application/pdf',
        filename='test.pdf',
        subject='Test'
    )
    assert message['threadId'] is None
    payload = base64.urlsafe_b64decode(message['raw'].encode())
    message = email.message_from_bytes(payload)
    assert message['to'] == to
    assert message['from'] == sender
    assert message['subject'] == 'Test'
    attachment = message.get_payload()[1]
    assert attachment['content-type'] == 'application/pdf'


@pytest.mark.django_db
def test_send_email(gmail_service, cv):
    send_email(gmail_service)

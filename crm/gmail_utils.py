import base64
import email
import logging
from datetime import datetime

import pytz
from django.conf import settings
from django.contrib.auth import get_user_model
from googleapiclient import discovery

from crm.utils import Credentials

logger = logging.getLogger('gmail_utils')


def parse_message(message):
    result = {
        "sent_at": datetime.utcfromtimestamp(int(message['internalDate']) / 1000).replace(tzinfo=pytz.utc),
    }
    msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
    mime_msg = email.message_from_bytes(msg_str)
    main_type = mime_msg.get_content_maintype()
    text = ""
    if main_type == 'multipart':
        for part in mime_msg.get_payload():
            charset = part.get_content_charset()
            if part.get_content_maintype() == 'text' and part.get_content_subtype() == 'plain':
                text = part.get_payload(decode=True).decode(charset, 'replace')
    elif main_type == 'text':
        text = mime_msg.get_payload()
    else:
        logger.error(f"Unknown main mime type {main_type}")
    result['text'] = text
    return result


def get_raw_messages(user):
    usa = user.social_auth.get(provider='google-oauth2')
    service = discovery.build('gmail', 'v1', credentials=Credentials(usa))

    labels = service.users().labels().list(userId='me').execute()
    try:
        label_id = next(
            label_info['id'] for label_info in labels['labels'] if label_info['name'] == settings.MAILBOX_LABEL
        )
    except StopIteration:
        logger.error(f"Can't find label with {settings.MAILBOX_LABEL}", code=127)
        return []

    # INBOX means a message is not archived
    mail = service.users().messages().list(userId='me', labelIds=[label_id, "INBOX"]).execute()
    message_ids = [message['id'] for message in mail['messages']]
    return [
        service.users().messages().get(userId='me',
                                       id=message_id, format='raw').execute()
        for message_id in message_ids
    ]


def sync():
    for user in get_user_model().objects.exclude(social_auth=None):
        raw_messages = get_raw_messages(user)
        parsed_messages = [
            parse_message(raw_message) for raw_message in raw_messages
        ]
        raise NotImplementedError(parsed_messages)

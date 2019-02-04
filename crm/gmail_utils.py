import base64
import email
import logging
from datetime import datetime

import pytz
from django.conf import settings
from django.contrib.auth import get_user_model
from googleapiclient import discovery

from crm.models import ProjectMessage, Employee, Recruiter, Project
from crm.utils import Credentials

logger = logging.getLogger('gmail_utils')


def remove_quotation(text):
    lines = text.splitlines()
    outer_quotation_started = False
    for i, line in enumerate(lines):
        if line.startswith(">"):
            if outer_quotation_started:
                return "\n".join(lines[:i])
            else:
                outer_quotation_started = True
    return text


def extract_text(email_message):
    main_type = email_message.get_content_maintype()
    if main_type == 'multipart':
        for part in email_message.get_payload():
            charset = part.get_content_charset()
            if part.get_content_maintype() == 'text':
                if part.get_content_subtype() == 'plain':
                    return part.get_payload(decode=True).decode(charset, 'replace')
            if part.get_content_maintype() == 'multipart':
                return extract_text(part)
    elif main_type == 'text':
        charset = email_message.get_content_charset()
        email_message.get_payload(decode=True).decode(charset, 'replace')
    else:
        logger.error(f"Unknown main mime type {main_type}")
        return ""


def parse_message(message):
    msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
    email_message = email.message_from_bytes(msg_str)
    from_address = email_message['from'][email_message['from'].index("<") + 1:-1]
    full_name = email_message['from'].replace(f"<{from_address}>", "").strip()
    result = {
        "sent_at": datetime.utcfromtimestamp(int(message['internalDate']) / 1000).replace(tzinfo=pytz.utc),
        "subject": email_message['subject'],
        "from_address": from_address,
        "full_name": full_name,
        "gmail_thread_id": message['threadId'],
        "gmail_message_id": message['id'],
    }
    text = extract_text(email_message)
    result['text'] = remove_quotation(text)
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
    message_ids = [message['id'] for message in mail.get('messages', [])]
    return [
        service.users().messages().get(userId='me',
                                       id=message_id, format='raw').execute()
        for message_id in message_ids
    ]


def ensure_manager(message):
    manager = Employee.objects.filter(email__iexact=message['from_address']).first()
    if not manager:
        domain = message['from_address'].split('@')[-1]
        company = Recruiter.objects.filter(url__icontains=domain).first()
        company = company or Recruiter.objects.create(
            name=domain.split(".")[0].capitalize(),
            url=f"http://{domain}"
        )
        try:
            first_name, last_name = message['full_name'].split(" ")
        except ValueError:
            first_name, last_name = "", message['last_name']
        manager, manager_created = Employee.objects.get_or_create(
            email=message['from_address'],
            defaults={
                "company": company,
                "first_name": first_name,
                "last_name": last_name,
            }
        )
    return manager


def ensure_project(message, manager):
    existing_messages = ProjectMessage.objects.filter(gmail_thread_id=message['gmail_thread_id'])

    if existing_messages:
        project = existing_messages.first().project
    else:
        project = Project.objects.exclude(
            state='stopped'
        ).filter(manager=manager).order_by('-modified').first()
        if not project:
            project, project_created = Project.objects.get_or_create(
                name=message['subject'],
                manager=manager,
                defaults={
                    "location": manager.company.location,
                    "original_description": message['text']
                }
            )
    return project


def associate(message):
    """
    Associates message with projects and people
    """
    already_processed = ProjectMessage.objects.filter(gmail_message_id=message['gmail_message_id']).first()
    if already_processed:
        return already_processed

    manager = ensure_manager(message)
    project = ensure_project(message, manager)

    return ProjectMessage.objects.create(
        text=message['text'],
        author=manager,
        project=project,
        subject=message['subject'],
        sent_at=message['sent_at'],
        gmail_message_id=message['gmail_message_id'],
        gmail_thread_id=message['gmail_thread_id']
    )


def sync():
    for user in get_user_model().objects.exclude(social_auth=None):
        raw_messages = get_raw_messages(user)
        parsed_messages = [
            parse_message(raw_message) for raw_message in raw_messages
        ]
        for message in parsed_messages:
            associate(message)

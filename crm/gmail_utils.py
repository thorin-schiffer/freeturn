import base64
import email
import logging
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import StringIO

import pytz
from django.conf import settings
from django.contrib.auth import get_user_model
from googleapiclient import discovery

from crm.models.company import Company
from crm.models.employee import Employee
from crm.models.project import Project
from crm.models.project_message import ProjectMessage
from crm.utils import Credentials

logger = logging.getLogger('gmail_utils')


def remove_quotation(text):
    lines = text.splitlines()
    outer_quotation_started = False
    for i, line in enumerate(lines):
        if line.startswith('>'):
            if outer_quotation_started:
                return '\n'.join(lines[:i])
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
        return email_message.get_payload(decode=True).decode(charset or 'utf-8', 'replace')
    else:
        logger.error(f'Unknown main mime type {main_type}')
        return ''


def parse_message(message):
    msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
    email_message = email.message_from_bytes(msg_str)
    if email_message['from']:
        from_address = email_message['from'][email_message['from'].index('<') + 1:-1]
        full_name = email_message['from'].replace(f'<{from_address}>', '').strip()
    else:
        from_address = 'unknown'
        full_name = 'unknown'

    result = {
        'sent_at': datetime.utcfromtimestamp(int(message['internalDate']) / 1000).replace(tzinfo=pytz.utc),
        'subject': email_message['subject'],
        'from_address': from_address,
        'full_name': full_name,
        'gmail_thread_id': message['threadId'],
        'gmail_message_id': message['id'],
    }
    text = extract_text(email_message)
    if text:
        result['text'] = remove_quotation(text)
    return result


def get_labels(service):
    return service.users().labels().list(userId='me').execute()


def get_message_ids(service, label_id):
    return service.users().messages().list(userId='me', labelIds=[label_id, 'INBOX']).execute()


def get_message_raws(service, message_id):
    return service.users().messages().get(userId='me',
                                          id=message_id, format='raw').execute()


def get_raw_messages(service):
    labels = get_labels(service)
    try:
        label_id = next(
            label_info['id'] for label_info in labels['labels'] if label_info['name'] == settings.MAILBOX_LABEL
        )
    except StopIteration:
        logger.error(f"Can't find label with {settings.MAILBOX_LABEL}")
        return []

    # INBOX means a message is not archived
    mail = get_message_ids(service, label_id)
    message_ids = [message['id'] for message in mail.get('messages', [])]
    return [
        get_message_raws(service, message_id)
        for message_id in message_ids
    ]


def ensure_manager(message):
    manager = Employee.objects.filter(email__iexact=message['from_address']).first()
    if not manager:
        domain = message['from_address'].split('@')[-1]
        company = Company.objects.filter(url__icontains=domain).first()
        company = company or Company.objects.create(
            name=domain.split('.')[0].capitalize(),
            url=f'http://{domain}'
        )
        try:
            first_name, last_name = message['full_name'].split(' ')
        except ValueError:
            first_name, last_name = '', message.get('last_name', '')
        manager, _ = Employee.objects.get_or_create(
            email=message['from_address'],
            defaults={
                'company': company,
                'first_name': first_name,
                'last_name': last_name,
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
                    'location': manager.company.location,
                    'original_description': message['text']
                }
            )
    return project


def associate(message):
    """
    Associates message with projects and people
    """
    already_processed = ProjectMessage.objects.filter(gmail_message_id=message['gmail_message_id']).first()
    if already_processed:
        return already_processed, False

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
    ), True


def sync():
    if not settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY:
        return []
    project_messages = []
    parsed_messages = []
    for user in get_user_model().objects.exclude(social_auth=None):
        usas = user.social_auth.filter(provider='google-oauth2')
        for usa in usas:
            creds = Credentials(usa)
            service = discovery.build('gmail', 'v1', credentials=creds)
            raw_messages = get_raw_messages(service)
            parsed_messages += [
                parse_message(raw_message) for raw_message in raw_messages
            ]

    for message in parsed_messages:
        project_message, created = associate(message)
        if created:
            project_messages.append(project_message)
            if not project_message.project.cvs.exists():
                project_message.project.create_cv(user)
    return project_messages


def create_message_with_attachment(sender, to, message_text_html,
                                   file,
                                   content_type, filename,
                                   encoding=None, reply_to=None, subject=None):
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    message['in-reply-to'] = reply_to

    message.attach(MIMEText(message_text_html, 'html'))

    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)

    if main_type == 'application' and sub_type == 'pdf':
        temp = open(file, 'rb')
        msg = MIMEApplication(temp.read(), _subtype=sub_type)
        temp.close()
    else:
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(file.read())
        file.close()
    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(msg)

    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}


def send_raw(service, user_id, message):
    message = service.users().messages().send(userId=user_id, body=message).execute()
    return message


def send_email(from_user, to_email, rich_text, cv, reply_to=None):
    if reply_to:
        raise NotImplementedError
    usa = from_user.social_auth.filter(provider='google-oauth2').first()
    creds = Credentials(usa)
    service = discovery.build('gmail', 'v1', credentials=creds)
    file = StringIO('1234566')

    message = create_message_with_attachment(
        sender=from_user.email,
        to=to_email,
        reply_to=reply_to,
        message_text_html=rich_text,
        file=file,
        subject='test',
        filename='test.txt',
        content_type='text/plain'
    )
    send_raw(service=service, user_id='thorin@schiffer.pro', message=message)

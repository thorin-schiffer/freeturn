import urllib.parse
from datetime import timedelta

import holidays
from django_mailbox.models import Mailbox


def get_working_days(start_date, end_date):
    days = [start_date + timedelta(days=1) * i for i in range(
        (end_date - start_date).days + 1
    )]

    working_days = []
    for day in days:
        if day in holidays.DE(prov='BE') or day.weekday() in [5, 6]:
            continue
        working_days.append(day)
    return working_days


def ensure_mailbox(backend, details, response, *args, **kwargs):
    # archive to inbox in order to keep emails on server
    # see https://github.com/coddingtonbear/django-mailbox/issues/72
    uri = f"gmail+ssl://{urllib.parse.quote_plus(details['email'])}:oauth2@imap.gmail.com?archive=Inbox&folder=CRM"
    name = details['username']
    from_email = details['email']
    Mailbox.objects.update_or_create(
        name=name,
        defaults={
            "uri": uri,
            "from_email": from_email
        }
    )

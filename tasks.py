import invoke
import functools
import os
import sys
import dotenv
from invoke import Exit

dotenv.load_dotenv()


def with_django(func):
    @functools.wraps(func)
    def _inner(context, *args, **kwargs):
        from django.core.wsgi import get_wsgi_application
        PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))

        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "portfolio.settings.dev")
        sys.path.append(PROJECT_DIR)
        get_wsgi_application()

        func(context, *args, **kwargs)

    return _inner


@invoke.task
def deploy(context, repo=True, db_backup=True):
    if db_backup:
        context.run("heroku pg:backups:capture ")
    if repo:
        context.run("git push origin && git push heroku develop:master")
    else:
        context.run("git push heroku develop:master")


@invoke.task
@with_django
def create_pages(context):
    from home.models import PortfolioPage, TechnologiesPage, HomePage
    from treebeard.exceptions import NodeAlreadySaved

    types = [PortfolioPage, TechnologiesPage]
    home = HomePage.objects.first()

    for t in types:
        if not t.objects.exists():
            print(f"Adding {t}")
            title = t.__name__.replace("Page", "").lower()
            try:
                home.add_child(instance=t(title=title))
            except NodeAlreadySaved:
                print(f"Error adding {title}, page is somehow there")
                continue


@invoke.task
def sync_production(ctx, backup=True):
    from portfolio.settings import production, production_local
    if backup:
        ctx.run("heroku pg:backups:capture")
    ctx.run("heroku pg:backups:download")
    database_url = os.environ['DATABASE_URL']
    ctx.run(f"pg_restore --verbose --clean --no-acl --no-owner --dbname={database_url} latest.dump")
    os.remove("latest.dump")
    ctx.run(
        f"aws s3 sync --acl public-read s3://{production.AWS_STORAGE_BUCKET_NAME} "
        f"s3://{production_local.AWS_STORAGE_BUCKET_NAME}"
    )


@invoke.task
@with_django
def mail(context):
    from googleapiclient import discovery
    from django.contrib.auth import get_user_model
    from django.conf import settings
    from crm.utils import Credentials

    user = get_user_model().objects.get(username='sergey')

    usa = user.social_auth.get(provider='google-oauth2')
    service = discovery.build('gmail', 'v1', credentials=Credentials(usa))

    labels = service.users().labels().list(userId='me').execute()
    try:
        label_id = next(
            label_info['id'] for label_info in labels['labels'] if label_info['name'] == settings.MAILBOX_LABEL
        )
    except StopIteration:
        raise Exit(f"Can't find label with {settings.MAILBOX_LABEL}", code=127)

    # INBOX means a message is not archived
    mail = service.users().messages().list(userId='me', labelIds=[label_id, "INBOX"]).execute()
    message_ids = [message['id'] for message in mail['messages']]
    messages = [
        service.users().messages().get(userId='me',
                                       id=message_id, format="raw").execute()
        for message_id in message_ids
    ]
    print(messages)

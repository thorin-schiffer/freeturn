import functools
import json
import logging
import os
import sys

import invoke
from invoke import Exit
import environ

logger = logging.getLogger(__file__)
env = environ.Env()
environ.Env.read_env('.env')


# https://github.com/pyinvoke/invoke/issues/555
def configure_django():
    from django.core.wsgi import get_wsgi_application
    PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "freeturn.settings")
    sys.path.append(PROJECT_DIR)
    get_wsgi_application()


def with_django(func):
    @functools.wraps(func)
    def _inner(context, *args, **kwargs):
        configure_django()
        func(context, *args, **kwargs)

    return _inner


@invoke.task(
    help={
        'repo': 'Push to your repo first',
        'db_backup': 'Backup the database before deployment'
    }
)
def deploy(context, repo=True, db_backup=True):
    """Deploy the project manually to heroku using git deployment, see https://devcenter.heroku.com/articles/git"""
    if db_backup:
        context.run("heroku pg:backups:capture ")
    if repo:
        context.run("git push origin && git push heroku develop:master")
    else:
        context.run("git push heroku develop:master")


@invoke.task
@with_django
def mail(context):
    """Simple mail check task, use in cron"""
    from crm.gmail_utils import sync
    sync()


@invoke.task
@with_django
def create_admin(ctx):
    """Creates admin for local instance"""
    assert getattr(ctx, 'host', 'localhost') == 'localhost'
    from django.contrib.auth import get_user_model

    if not get_user_model().objects.filter(username='admin').exists():
        user = get_user_model().objects.create_superuser(
            'admin', 'admin@admin.com', 'admin'
        )
        print(f"Created user {user} with password 'admin'")


@invoke.task
def fill(context):
    """Fill the database with test fixtures , won't work in non debug envs"""
    configure_django()
    import filler
    from django.conf import settings
    if not settings.DEBUG:
        print("Won't fill in non debug envs, possible data loss or corruption")
        return

    filler.clean()
    create_admin(context)
    filler.fill()


@invoke.task
def update(context):
    """Updates code from gitlab and reinstalls pipenv deps"""
    context.run(f"pipenv clean")
    # https://github.com/pypa/pipenv/issues/3493
    context.run(f"pipenv install --ignore-pipfile --deploy --dev")


@invoke.task
def collect_static(context, local=False):
    """Django collect static"""
    print("Collecting static...")
    context.run(f"./manage.py collectstatic --noinput -v 0")


@invoke.task(help={
    "make": "update *.mo translation file before parsing (makemessages)"
})
def i18n(ctx):
    """Runs django translation routines"""
    print("Collecting i18n")
    ctx.run(f"./manage.py makemessages -i 'venv/*' -l de")
    ctx.run(f"./manage.py compilemessages -l de")


@invoke.task
def install_hooks(context):
    """Installs pre-commit hooks"""
    print("Installing pre-commit hook")
    context.run(f"pre-commit install")


@invoke.task
def validate_ci_config(context):
    """Check circle ci config"""
    context.run("circleci config validate")


@invoke.task(default=True)
def bootstrap(context):
    """Local bootstrap for development in non-containerized env"""
    configure_django()
    from django.conf import settings
    if not settings.DEBUG:
        Exit("Won't bootstrap in non dev env")
    update(context)
    fill(context, migrate=True)
    collect_static(context)
    i18n(context)
    install_hooks(context)


@invoke.task(
    help={
        "fill": "Fixtures the database",
        "host": "Host to bind"
    }
)
def unicorn(context, fill_db=False, host=None):
    """Starts gunicorn as webserver"""
    if fill_db or os.getenv("FILL_DB", None):
        fill(context)
    if host:
        context.run(f"gunicorn freeturn.wsgi --log-file - -b {host}")
    else:
        context.run("gunicorn freeturn.wsgi --log-file -")


@invoke.task(
    help={
        "review_url": "Review URL from heroku, defaults to $REVIEW_URL"
    }
)
def browserstack(context, review_url=None):
    config_path = os.path.join("acceptance_tests", "browserstack_capabilities.json")
    with open(config_path, "r") as f:
        capabilities = json.load(f)
    branch = os.getenv("CIRCLE_BRANCH", context.run("git rev-parse --abbrev-ref HEAD").stdout.strip())
    sha = os.getenv("CIRCLE_SHA1", context.run("git rev-parse HEAD").stdout.strip())
    capabilities.update({
        "build": f"{branch}:{sha}"
    })
    capabilities_string = " ".join([
        f"--capability {key} \"{value}\""
        for key, value in capabilities.items()
    ])

    review_url = review_url or os.getenv("REVIEW_URL")
    command = f"pytest --driver BrowserStack --base-url \"{review_url}\" " \
              f"{capabilities_string} " \
              f"acceptance_tests/"
    print(command)
    context.run(command)


@invoke.task
def install_s3_policy(context):
    configure_django()
    from aws_utils import install_storage_policy
    from django.core.exceptions import ImproperlyConfigured

    try:
        response = install_storage_policy()
    except ImproperlyConfigured:
        raise Exit("Can't install s3 policy, s3 is not configured"
                   "set bucket, user and account in env, see .env_template for info", code=127)
    print(response)

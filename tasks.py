import functools
import logging
import os
import sys

import dotenv
import invoke

dotenv.load_dotenv()
logger = logging.getLogger(__file__)


# https://github.com/pyinvoke/invoke/issues/555
def configure_django():
    from django.db.backends.base.base import BaseDatabaseWrapper
    BaseDatabaseWrapper.queries_limit = 50000
    from django.core.wsgi import get_wsgi_application
    PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rms.settings")
    sys.path.append(PROJECT_DIR)
    get_wsgi_application()


def with_django(func):
    @functools.wraps(func)
    def _inner(context, *args, **kwargs):
        configure_django()
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
def sync_production_db(ctx, backup=True):
    # if backup:
    #     ctx.run("heroku pg:backups:capture")
    # ctx.run("heroku pg:backups:download")
    database_url = os.environ['DATABASE_URL']
    ctx.run(f"pg_restore --verbose --clean --no-acl --no-owner --dbname={database_url} latest.dump")
    os.remove("latest.dump")


@invoke.task
def sync_production_s3(ctx):
    from portfolio.settings import production, production_local
    ctx.run(
        f"aws s3 sync --acl public-read s3://{production.AWS_STORAGE_BUCKET_NAME} "
        f"s3://{production_local.AWS_STORAGE_BUCKET_NAME}"
    )


@invoke.task
@with_django
def mail(context):
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


def fill_pages(projects_count=9):
    from wagtail.core.models import Page
    from home.factories import HomePageFactory, PortfolioPageFactory, TechnologiesPageFactory, ProjectPageFactory
    from home.models import Technology, Responsibility
    from wagtail.images.models import Image
    from home.factories import SiteFactory

    home = HomePageFactory.build(picture=None)
    default_site = SiteFactory(is_default_site=True)
    root = Page.objects.get(pk=1)
    root.add_child(instance=home)
    default_site.root_page.delete()
    default_site.root_page = home
    default_site.port = 8000
    default_site.save()

    portfolio_page = PortfolioPageFactory.build()
    home.add_child(instance=portfolio_page)
    images = Image.objects.all()
    for i in range(projects_count):
        logo = images[i % len(images)]
        page = ProjectPageFactory.build(technologies=[],
                                        description__max_nb_chars=1000,
                                        logo=logo)
        portfolio_page.add_child(instance=page)

        page.responsibilities.set(Responsibility.objects.order_by("?")[:3])
        page.technologies.set(Technology.objects.order_by("?")[:3])
        page.save()

        print(f"Added {page}")

    technologies_page = TechnologiesPageFactory.build()
    home.add_child(instance=technologies_page)


def fill_snippets(count=10):
    from home.factories import TechnologyFactory, ResponsibilityFactory
    from wagtail.images.models import Image
    for i in range(count):
        random_image = Image.objects.order_by("?").first()
        print(f"Adding: {TechnologyFactory(logo=random_image)}")
        print(f"Adding: {ResponsibilityFactory()}")


def fill_crm_data():
    pass


def fill_pictures():
    from django.core.files.images import ImageFile
    from wagtail.images.models import Image
    from wagtail_factories import CollectionFactory
    from wagtail.core.models import Collection

    images_path = "fill_media"
    directories = [filename for filename in os.listdir(images_path)]
    for directory in directories:
        collection = Collection.objects.filter(name=directory.capitalize()).first() or \
            CollectionFactory(name=directory.capitalize())
        filenames = [filename for filename in os.listdir(os.path.join(images_path, directory))
                     if filename.endswith('.png')]

        for filename in filenames:
            full_path = os.path.join(images_path, directory, filename)
            with open(full_path, 'rb') as f:
                image_file = ImageFile(f, name=filename)
                image = Image(file=image_file, title=filename)
                image.collection = collection
                image.save()
        print(f"Loaded {Image.objects.count()} images")


def fill_forms():
    pass


def fill_clean():
    from wagtail.images.models import Image
    from home.models import Technology, Responsibility, HomePage
    from wagtail.core.models import Site

    Image.objects.all().delete()
    Technology.objects.all().delete()
    Responsibility.objects.all().delete()
    HomePage.objects.all().delete()
    Site.objects.all().delete()


@invoke.task(help={
    'migrate': 'Migrate DB and remove the datbase file before filling',
})
def fill(context, migrate=False):
    import factory.random
    factory.random.reseed_random('my_awesome_project')
    configure_django()
    if migrate:
        context.run('rm db.sqlite3')
        context.run('PYTHONUNBUFFERED=1 ./manage.py migrate')
        create_admin(context)
    else:
        fill_clean()
    fill_pictures()
    fill_snippets()
    fill_pages()

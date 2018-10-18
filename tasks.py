import invoke
import functools
import os
import sys


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
def deploy(context, repo=True):
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

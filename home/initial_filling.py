import logging

from wagtail.core.models import Page
from wagtail.users.forms import User

from home.factories import HomePageFactory, PortfolioPageFactory, TechnologiesPageFactory

logger = logging.getLogger(__file__)


def fill_pages():
    from wagtail.core.models import Site
    admin = User.objects.get(username='admin')
    factories = [PortfolioPageFactory, TechnologiesPageFactory]
    home = HomePageFactory.build(picture=None, owner=admin)
    default_site = Site.objects.last()
    root = Page.objects.get(pk=1)
    root.add_child(instance=home)
    default_site.root_page = home
    default_site.port = 8000
    default_site.save()

    for factory_class in factories:
        logger.info(f"Adding {factory_class}")
        home.add_child(instance=factory_class.build(owner=admin))


def fill_snippets():
    pass


def fill_crm_data():
    pass


def fill_pictures():
    pass


def fill_forms():
    pass


def fill():
    fill_pages()

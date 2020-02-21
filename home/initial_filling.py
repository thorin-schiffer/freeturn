import logging

from home.factories import HomePageFactory, PortfolioPageFactory, TechnologiesPageFactory

logger = logging.getLogger(__file__)


def fill_pages():
    from wagtail.core.models import Site
    factories = [PortfolioPageFactory, TechnologiesPageFactory]
    home = HomePageFactory.build(picture=None)
    default_site = Site.objects.last()
    default_site.root_page.add_child(instance=home)

    for factory_class in factories:
        logger.info(f"Adding {factory_class}")
        home.add_child(instance=factory_class.build())


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

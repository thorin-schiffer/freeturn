from home.models import PortfolioPage, TechnologiesPage, HomePage
import logging

logger = logging.getLogger(__file__)


def fill_pages():
    from treebeard.exceptions import NodeAlreadySaved

    types = [PortfolioPage, TechnologiesPage]
    home = HomePage.objects.first()

    for t in types:
        if not t.objects.exists():
            logger.info(f"Adding {t}")
            title = t.__name__.replace("Page", "").lower()
            try:
                home.add_child(instance=t(title=title))
            except NodeAlreadySaved:
                logger.warning(f"Can't add {title}, page is already there")
                continue


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

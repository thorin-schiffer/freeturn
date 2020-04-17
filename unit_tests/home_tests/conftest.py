import pytest
import wagtail_factories
from pytest_factoryboy import register

from home import factories

register(factories.HomePageFactory)
register(wagtail_factories.ImageFactory)
register(wagtail_factories.CollectionFactory)
register(factories.ContactPageFactory)
register(factories.ProjectPageFactory)
register(factories.PortfolioPageFactory)
register(factories.TagFactory)
register(factories.TechnologyFactory)
register(factories.TechnologiesPageFactory)
register(factories.SiteFactory)


@pytest.fixture(autouse=True)
def default_site(site_factory):
    return site_factory.create(is_default_site=True)

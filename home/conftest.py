from pytest_factoryboy import register

from home import factories

register(factories.HomePageFactory)
register(factories.ContactPageFactory)
register(factories.ProjectPageFactory)
register(factories.PortfolioPageFactory)

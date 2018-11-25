from pytest_factoryboy import register
from crm import factories

register(factories.CityFactory)
register(factories.EmployeeFactory)
register(factories.ChannelFactory)
register(factories.RecruiterFactory)
register(factories.ProjectFactory)
register(factories.ClientCompanyFactory)
register(factories.MailboxFactory)

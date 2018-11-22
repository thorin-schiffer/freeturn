import factory

from crm import models


class CityFactory(factory.DjangoModelFactory):
    name = factory.Faker('city')

    class Meta:
        model = models.City


class ChannelFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"channel {n}")
    url = factory.Faker('uri')

    class Meta:
        model = models.Channel


class BaseCompanyFactory(factory.DjangoModelFactory):
    name = factory.Faker('company')
    location = factory.SubFactory(CityFactory)
    channel = factory.SubFactory(ChannelFactory)
    url = factory.Faker('uri')

    class Meta:
        abstract = True


class RecruiterFactory(BaseCompanyFactory):
    class Meta:
        model = models.Recruiter


class EmployeeFactory(factory.DjangoModelFactory):
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    telephone = factory.Faker('phone_number')

    company = factory.SubFactory(RecruiterFactory)

    class Meta:
        model = models.Employee

import factory

from crm import models


class CityFactory(factory.DjangoModelFactory):
    name = factory.Faker('city')

    class Meta:
        model = models.City

import factory
import wagtail_factories
from django.utils.timezone import get_current_timezone
from taggit.models import Tag
from wagtail.core.models import Site

from home import models
from home.models import Technology, Responsibility


class HomePageFactory(wagtail_factories.PageFactory):
    title = factory.Faker('name')
    picture = factory.SubFactory(wagtail_factories.ImageFactory)

    class Meta:
        model = models.HomePage


class ContactPageFactory(wagtail_factories.PageFactory):
    title = "Contact"
    show_on_home = True

    class Meta:
        model = models.ContactPage


class ProjectPageFactory(wagtail_factories.PageFactory):
    title = factory.Faker('company')
    summary = factory.Faker('sentence')
    description = factory.Faker('text')
    position = factory.Faker('job')
    start_date = factory.Faker('past_date', start_date="-10y", tzinfo=get_current_timezone())
    duration = 6

    @factory.post_generation
    def technologies(self, created, extracted, *args, **kwargs):
        if extracted is not None:
            technologies = [TechnologyFactory(name=name) for name in extracted]
        else:
            technologies = [TechnologyFactory()]
        for technology in technologies:
            self.technologies.add(technology)
        if technologies:
            self.save()

    class Meta:
        model = models.ProjectPage


class PortfolioPageFactory(wagtail_factories.PageFactory):
    title = "Portfolio"

    class Meta:
        model = models.PortfolioPage


class TagFactory(factory.DjangoModelFactory):
    name = factory.Faker("word")

    class Meta:
        model = Tag


class TechnologyFactory(factory.DjangoModelFactory):

    name = factory.Faker("word")
    summary = factory.Faker("sentence")

    class Meta:
        model = Technology
        django_get_or_create = ('name',)


class TechnologiesPageFactory(wagtail_factories.PageFactory):
    title = "Technologies"

    class Meta:
        model = models.TechnologiesPage


class SiteFactory(factory.DjangoModelFactory):
    hostname = 'testsite'
    port = 8000
    site_name = factory.Faker('sentence')
    root_page = factory.SubFactory(wagtail_factories.PageFactory)

    class Meta:
        model = Site


class ResponsibilityFactory(factory.DjangoModelFactory):
    text = factory.Faker('sentence')

    class Meta:
        model = Responsibility

import factory
import wagtail_factories
from taggit.models import Tag
from wagtail.core.models import Page, Site

from home import models
from home.models import TechnologyInfo


class HomePageFactory(wagtail_factories.PageFactory):
    title = factory.Faker('sentence')

    class Meta:
        model = models.HomePage

    @factory.post_generation
    def add_to_tree(self, *args, **kwargs):
        root = Page.objects.filter(title='root').first()
        self.parent = root


class ContactPageFactory(wagtail_factories.PageFactory):
    title = "Contact"

    class Meta:
        model = models.ContactPage


class ProjectPageFactory(wagtail_factories.PageFactory):
    summary = factory.Faker('sentence')
    description = factory.Faker('text')
    responsibility = factory.Faker('word')
    start_date = factory.Faker('past_datetime', start_date="-15d")

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


class TechnologyInfoFactory(factory.DjangoModelFactory):
    tag = factory.SubFactory(TagFactory)

    class Meta:
        model = TechnologyInfo


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

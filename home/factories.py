import factory
import wagtail_factories
from wagtail.core.models import Page

from home import models


class HomePageFactory(wagtail_factories.PageFactory):
    title = factory.Faker('sentence')

    class Meta:
        model = models.HomePage

    @factory.post_generation
    def add_to_tree(self, *args, **kwargs):
        root = Page.objects.filter(title='root').first()
        self.parent = root


class ContactPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = models.ContactPage


class ProjectPageFactory(wagtail_factories.PageFactory):
    summary = factory.Faker('sentence')
    description = factory.Faker('text')
    responsibility = factory.Faker('word')
    start_date = factory.Faker('past_datetime')

    class Meta:
        model = models.ProjectPage

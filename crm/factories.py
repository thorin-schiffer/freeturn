import uuid
from datetime import timedelta

import factory
import wagtail_factories
from django.contrib.auth import get_user_model
from django.utils.timezone import get_current_timezone
from social_django.models import UserSocialAuth

from crm import models
from crm.models import wrap_table_data
from home.factories import ProjectPageFactory, TechnologyFactory


class CityFactory(factory.DjangoModelFactory):
    name = factory.Faker('city')

    class Meta:
        model = models.City
        django_get_or_create = ('name',)


class ChannelFactory(factory.DjangoModelFactory):
    name = factory.Faker('sentence')
    url = factory.Faker('uri')

    class Meta:
        model = models.Channel


class CompanyFactory(factory.DjangoModelFactory):
    name = factory.Faker('company')
    location = factory.SubFactory(CityFactory)
    channel = factory.SubFactory(ChannelFactory)
    url = factory.Faker('uri')
    logo = factory.SubFactory(wagtail_factories.ImageFactory)
    payment_address = factory.Faker('address')
    vat_id = factory.Sequence(lambda n: f"VAT-00000{n}")

    class Meta:
        model = models.Company
        django_get_or_create = ('name',)


class EmployeeFactory(factory.DjangoModelFactory):
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    telephone = factory.Faker('phone_number')

    company = factory.SubFactory(CompanyFactory)
    email = factory.Faker('email')

    class Meta:
        model = models.Employee


class ProjectFactory(factory.DjangoModelFactory):
    company = factory.SubFactory(CompanyFactory)
    manager = factory.SubFactory(EmployeeFactory)
    location = factory.SubFactory(CityFactory)
    original_description = factory.Faker('text')
    original_url = factory.Faker('uri')
    notes = factory.Faker('text')
    daily_rate = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    start_date = factory.Faker('future_datetime', end_date="+30d")
    name = factory.Faker('job')

    class Meta:
        model = models.Project

    @factory.post_generation
    def end_date(self, *args, **kwargs):
        if self.start_date:
            self.end_date = self.start_date + timedelta(days=90)


class ProjectMessageFactory(factory.DjangoModelFactory):
    project = factory.SubFactory(ProjectFactory)
    author = factory.SubFactory(EmployeeFactory)
    text = factory.Faker('text')
    gmail_message_id = factory.LazyAttribute(lambda x: str(uuid.uuid4()))
    gmail_thread_id = factory.LazyAttribute(lambda x: str(uuid.uuid4()))

    class Meta:
        model = models.ProjectMessage


class UserFactory(factory.DjangoModelFactory):
    username = factory.Sequence(lambda n: f"user{n}")

    class Meta:
        model = get_user_model()


class AdminFactory(UserFactory):
    is_staff = True
    is_superuser = True


class UserSocialAuthFactory(factory.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    provider = 'google-oauth2'
    extra_data = {
        'access_token': 'xyz',
        'refresh_token': 'xyz',
        'expires_in': 100
    }

    class Meta:
        model = UserSocialAuth


class CVFactory(factory.DjangoModelFactory):
    project = factory.SubFactory(ProjectFactory)
    earliest_available = factory.Faker('past_date', start_date="-15d", tzinfo=get_current_timezone())
    full_name = factory.Faker('name')
    title = factory.Faker('sentence')
    experience_overview = factory.Faker('text')
    education_overview = factory.Faker('text')
    contact_details = factory.Faker('phone_number')
    rate_overview = "100 schmeckles"
    working_permit = "permanent"

    class Meta:
        model = models.CV


class CVWithRelevantFactory(CVFactory):

    @factory.post_generation
    def relevant_skills(self, created, extracted, **kwargs):
        if extracted:
            raise NotImplementedError()
        self.relevant_skills.set([TechnologyFactory()])

    @factory.post_generation
    def relevant_projects(self, created, extracted, **kwargs):
        if extracted:
            raise NotImplementedError()
        self.relevant_project_pages.set([ProjectPageFactory()])


class InvoiceFactory(factory.DjangoModelFactory):
    project = factory.SubFactory(ProjectFactory)
    receiver_vat_id = factory.Sequence(lambda n: f"VAT-00000{n}")
    issued_date = factory.Faker('past_datetime')
    delivery_date = factory.Faker('past_datetime')
    tax_id = factory.Sequence(lambda n: f"TAX-00000{n}")
    bank_account = factory.Faker('iban')
    contact_data = factory.Faker('email')
    logo = factory.SubFactory(wagtail_factories.ImageFactory)

    class Meta:
        model = models.Invoice

    @factory.post_generation
    def positions(self, instance, create, *args, **kwargs):
        self.positions = wrap_table_data(models.Invoice.get_initial_positions())

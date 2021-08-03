import uuid
from datetime import timedelta

import factory
import wagtail_factories
from django.contrib.auth import get_user_model
from django.utils.timezone import get_current_timezone
from social_django.models import UserSocialAuth

import crm.models.city
import crm.models.company
import crm.models.cv
import crm.models.employee
import crm.models.invoice
import crm.models.project
import crm.models.project_message
from crm.models import MessageTemplate
from crm.models.invoice import wrap_table_data
from home.factories import ProjectPageFactory, TechnologyFactory


class CityFactory(factory.DjangoModelFactory):
    name = factory.Faker('city')

    class Meta:
        model = crm.models.city.City
        django_get_or_create = ('name',)


class CompanyFactory(factory.DjangoModelFactory):
    name = factory.Faker('company')
    location = factory.SubFactory(CityFactory)
    url = factory.Faker('uri')
    logo = factory.SubFactory(wagtail_factories.ImageFactory)
    payment_address = factory.Faker('address')
    vat_id = factory.Sequence(lambda n: f'VAT-00000{n}')

    class Meta:
        model = crm.models.company.Company
        django_get_or_create = ('name',)


class EmployeeFactory(factory.DjangoModelFactory):
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    telephone = factory.Faker('phone_number')

    company = factory.SubFactory(CompanyFactory)
    email = factory.Faker('email')

    class Meta:
        model = crm.models.employee.Employee


class ProjectFactory(factory.DjangoModelFactory):
    company = factory.SubFactory(CompanyFactory)
    manager = factory.SubFactory(EmployeeFactory)
    location = factory.SubFactory(CityFactory)
    original_description = factory.Faker('text')
    original_url = factory.Faker('uri')
    notes = factory.Faker('text')
    daily_rate = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    start_date = factory.Faker('future_datetime', end_date='+30d')
    name = factory.Faker('job')

    class Meta:
        model = crm.models.project.Project

    @factory.post_generation
    def generate_end_date(self, *args, **kwargs):
        if self.start_date:
            self.end_date = self.start_date + timedelta(days=90)


class ProjectMessageFactory(factory.DjangoModelFactory):
    project = factory.SubFactory(ProjectFactory)
    author = factory.SubFactory(EmployeeFactory)
    text = factory.Faker('text')
    subject = factory.Faker('sentence')
    gmail_message_id = factory.LazyAttribute(lambda x: str(uuid.uuid4()))
    gmail_thread_id = factory.LazyAttribute(lambda x: str(uuid.uuid4()))

    class Meta:
        model = crm.models.project_message.ProjectMessage


class UserFactory(factory.DjangoModelFactory):
    username = factory.Sequence(lambda n: f'user{n}')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')

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
        'expires': 100
    }
    uid = factory.Sequence(lambda n: f'uid_{n}')

    class Meta:
        model = UserSocialAuth


class CVFactory(factory.DjangoModelFactory):
    project = factory.SubFactory(ProjectFactory)
    earliest_available = factory.Faker('past_date', start_date='-15d', tzinfo=get_current_timezone())
    full_name = factory.Faker('name')
    title = factory.Faker('sentence')
    experience_overview = factory.Faker('text')
    education_overview = factory.Faker('text')
    contact_details = factory.Faker('phone_number')
    rate_overview = '100 schmeckles'
    working_permit = 'permanent'
    languages_overview = 'Lhammas: fluent'
    include_portfolio = True

    class Meta:
        model = crm.models.cv.CV


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

    @factory.post_generation
    def highlighted_projects(self, created, extracted, **kwargs):
        if extracted:
            raise NotImplementedError()
        self.highlighted_project_pages.set(self.relevant_project_pages.order_by('?'))


class InvoiceFactory(factory.DjangoModelFactory):
    project = factory.SubFactory(ProjectFactory)
    receiver_vat_id = factory.Sequence(lambda n: f'VAT-00000{n}')
    issued_date = factory.Faker('past_datetime')
    delivery_date = factory.Faker('past_datetime')
    tax_id = factory.Sequence(lambda n: f'TAX-00000{n}')
    bank_account = factory.Faker('iban')
    contact_data = factory.Faker('email')
    logo = factory.SubFactory(wagtail_factories.ImageFactory)

    class Meta:
        model = crm.models.invoice.Invoice

    @factory.post_generation
    def generate_positions(self, *args, **kwargs):
        self.positions = wrap_table_data(crm.models.invoice.Invoice.get_initial_positions())


class MessageTemplateFactory(factory.DjangoModelFactory):
    text = factory.Faker('text')
    state_transition = 'scope'
    name = factory.Sequence(lambda n: f'Template {n}')

    class Meta:
        model = MessageTemplate

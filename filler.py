import os
import random
from datetime import timedelta

from django.core.files.images import ImageFile
from django.db import transaction
from django.utils.timezone import make_aware
from wagtail.core.models import Collection
from wagtail.core.models import Page
from wagtail.core.models import Site
from wagtail.images.models import Image
from wagtail_factories import CollectionFactory

from crm.factories import ProjectFactory, CVFactory, ProjectMessageFactory, InvoiceFactory, MessageTemplateFactory
from crm.models import Project, Employee, get_project_state_transitions, MessageTemplate
from home.factories import HomePageFactory, TechnologiesPageFactory, \
    ContactPageFactory
from home.factories import PortfolioPageFactory, ProjectPageFactory
from home.factories import SiteFactory
from home.factories import TechnologyFactory, ResponsibilityFactory
from home.models import HomePage, FormField, ProjectPage
from home.models.snippets import Technology, Responsibility


def get_random_image(collection):
    return Image.objects.filter(collection__name__iexact=collection).order_by('?').first()


def fill_form(home):
    contact_page = ContactPageFactory.build()
    contact_page.form_fields = [
        FormField(label='your email', field_type='email', default_value='thorin@schiffer.pro'),
        FormField(label='some words about your project', field_type='multiline', required=False,
                  default_value='some words'),
        FormField(label='technologies', field_type='singleline',
                  default_value='Python'),
        FormField(label='workload (hours per week)', field_type='number', default_value=40),
        FormField(label='duration in months', field_type='number', default_value=6),
        FormField(label='location', field_type='singleline', default_value='Berlin'),
        FormField(label='privacy policy', field_type='checkbox'),
    ]
    home.add_child(instance=contact_page)


def fill_portfolio(home, projects_count=9):
    background = get_random_image('Backgrounds')
    portfolio_page = PortfolioPageFactory.build(background=background)
    home.add_child(instance=portfolio_page)
    logos_collection = Collection.objects.get(name='Logos')
    logos = Image.objects.filter(collection=logos_collection)
    for i in range(projects_count):
        logo = logos[i % len(logos)]
        page = ProjectPageFactory.build(technologies=[],
                                        description__max_nb_chars=1000,
                                        logo=logo)
        portfolio_page.add_child(instance=page)

        page.responsibilities.set(Responsibility.objects.order_by('?')[:3])
        page.technologies.set(Technology.objects.order_by('?')[:3])
        page.save()

        print(f'Added {page}')

    # issue 35
    page = ProjectPageFactory.build(technologies=[],
                                    title='No logo project',
                                    description__max_nb_chars=1000,
                                    logo=None)
    portfolio_page.add_child(instance=page)
    page.responsibilities.set(Responsibility.objects.order_by('?')[:3])
    page.technologies.set(Technology.objects.order_by('?')[:3])
    page.save()


def fill_pages():
    backgrounds_collection = Collection.objects.get(name='Backgrounds')
    backgrounds = Image.objects.filter(collection=backgrounds_collection)
    people_collection = Collection.objects.get(name='People')

    home = HomePageFactory.build(background=random.choice(backgrounds),
                                 picture=Image.objects.filter(collection=people_collection).order_by('?').first(),
                                 stackoverflow_profile='https://stackoverflow.com/users/1205242/eviltnan',
                                 github_profile='https://github.com/eviltnan',
                                 linkedin_profile='https://www.linkedin.com/in/thorin-schiffer/')
    heroku_app_name = os.getenv('HEROKU_APP_NAME')
    hostname = f'{heroku_app_name}.herokuapp.com' if heroku_app_name else 'localhost'
    default_site = SiteFactory(is_default_site=True, hostname=hostname)
    root = Page.objects.get(pk=1)
    root.add_child(instance=home)
    default_site.root_page.delete()
    default_site.root_page = home
    default_site.port = 80 if heroku_app_name else 8000
    default_site.save()

    fill_portfolio(home)

    technologies_page = TechnologiesPageFactory.build(background=random.choice(backgrounds))
    home.add_child(instance=technologies_page)

    fill_form(home)


def fill_snippets(count=10):
    for i in range(count):
        random_image = Image.objects.filter(collection__name='Logos').order_by('?').first()
        print(f'Adding: {TechnologyFactory(logo=random_image)}')
        print(f'Adding: {ResponsibilityFactory()}')


def make_project(**overloads):
    project = ProjectFactory(company__logo=None, manager__picture=None, manager__company__logo=None, **overloads)
    project.company.logo = get_random_image('Logos')
    project.company.save()
    project.manager.picture = get_random_image('People')
    project.manager.save()
    project.modified = make_aware(project.start_date) - timedelta(days=random.randint(30, 90))
    project.save(update_modified=False)
    print(f'Created {project}')
    return project


def fill_crm_data(projects_count=5):
    for i in range(projects_count):
        project = make_project()
        cv = CVFactory(project=project, picture=None)
        cv.picture = get_random_image('People')
        cv.save()
        cv.relevant_project_pages.set(ProjectPage.objects.order_by('?')[:3])
        cv.relevant_skills.set(Technology.objects.order_by('?')[:3])
        ProjectMessageFactory(project=project, author=project.manager)
        InvoiceFactory(project=project, logo=project.company.logo)

    # CV without portfolio
    without_portfolio = CVFactory(include_portfolio=False,
                                  project=make_project(name='Project without portfolio flag with all projects'),
                                  project_listing_title='Projects')
    without_portfolio.relevant_project_pages.set(ProjectPage.objects.all())
    without_portfolio.picture = get_random_image('People')
    without_portfolio.save()
    without_portfolio.relevant_skills.set(Technology.objects.order_by('?')[:3])

    # all projects with portfolio
    all_projects = CVFactory(project=make_project(name='All projects'))
    all_projects.relevant_project_pages.set(ProjectPage.objects.all())
    all_projects.picture = get_random_image('People')
    all_projects.save()
    all_projects.relevant_skills.set(Technology.objects.order_by('?')[:3])

    for transition in get_project_state_transitions():
        MessageTemplateFactory(state_transition=transition[0])
    make_project(original_description='Das ist eine Projektbeschreibung',
                 name='Ein deutschsprachiges Projekt')


def fill_pictures():
    images_path = 'fill_media'
    directories = [filename for filename in os.listdir(images_path)]
    root_collection = Collection.get_first_root_node() or CollectionFactory(name='Root')
    for directory in directories:
        name = directory.capitalize()
        collection = Collection.objects.filter(name=name).first() or root_collection.add_child(name=name)
        filenames = [filename for filename in os.listdir(os.path.join(images_path, directory))]

        for filename in filenames:
            full_path = os.path.join(images_path, directory, filename)
            with open(full_path, 'rb') as f:
                image_file = ImageFile(f, name=filename)
                image = Image(file=image_file, title=filename)
                image.collection = collection
                image.save()
        print(f'Loaded {Image.objects.count()} images from {directory}')


def clean():
    Image.objects.all().delete()
    Technology.objects.all().delete()
    Responsibility.objects.all().delete()
    Page.objects.exclude(pk=1).delete()
    HomePage.objects.all().delete()
    Site.objects.all().delete()
    Project.objects.all().delete()
    Employee.objects.all().delete()
    Collection.objects.all().delete()
    MessageTemplate.objects.all().delete()


@transaction.atomic
def fill():
    import factory.random
    factory.random.reseed_random('my_awesome_project')
    fill_pictures()
    fill_snippets()
    fill_pages()
    fill_crm_data()

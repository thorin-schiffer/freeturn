import os
import random


def fill_portfolio(home, projects_count=9):
    from wagtail.images.models import Image
    from wagtail.core.models import Collection
    from home.factories import PortfolioPageFactory, ProjectPageFactory
    from home.models import Technology, Responsibility
    background = Image.objects.filter(collection__name='Backgrounds').order_by("?").first()
    portfolio_page = PortfolioPageFactory.build(background=random.choice(background))
    home.add_child(instance=portfolio_page)
    logos_collection = Collection.objects.get(name='Logos')
    logos = Image.objects.filter(collection=logos_collection)
    for i in range(projects_count):
        logo = logos[i % len(logos)]
        page = ProjectPageFactory.build(technologies=[],
                                        description__max_nb_chars=1000,
                                        logo=logo)
        portfolio_page.add_child(instance=page)

        page.responsibilities.set(Responsibility.objects.order_by("?")[:3])
        page.technologies.set(Technology.objects.order_by("?")[:3])
        page.save()

        print(f"Added {page}")


def fill_pages():
    from wagtail.core.models import Page
    from home.factories import HomePageFactory, TechnologiesPageFactory, \
        ContactPageFactory
    from wagtail.images.models import Image
    from home.factories import SiteFactory
    from wagtail.core.models import Collection
    backgrounds_collection = Collection.objects.get(name='Backgrounds')
    backgrounds = Image.objects.filter(collection=backgrounds_collection)
    people_collection = Collection.objects.get(name='People')

    home = HomePageFactory.build(background=random.choice(backgrounds),
                                 picture=Image.objects.filter(collection=people_collection).order_by("?").first(),
                                 stackoverflow_profile='https://stackoverflow.com/users/1205242/eviltnan',
                                 github_profile='https://github.com/eviltnan',
                                 linkedin_profile='https://www.linkedin.com/in/sergey-cheparev/')
    default_site = SiteFactory(is_default_site=True)
    root = Page.objects.get(pk=1)
    root.add_child(instance=home)
    default_site.root_page.delete()
    default_site.root_page = home
    default_site.port = 8000
    default_site.save()

    fill_portfolio(home)
    technologies_page = TechnologiesPageFactory.build(background=random.choice(backgrounds))
    home.add_child(instance=technologies_page)

    home.add_child(instance=ContactPageFactory.build())


def fill_snippets(count=10):
    from home.factories import TechnologyFactory, ResponsibilityFactory
    from wagtail.images.models import Image
    for i in range(count):
        random_image = Image.objects.filter(collection__name='Logos').order_by("?").first()
        print(f"Adding: {TechnologyFactory(logo=random_image)}")
        print(f"Adding: {ResponsibilityFactory()}")


def fill_crm_data():
    pass


def fill_pictures():
    from django.core.files.images import ImageFile
    from wagtail.images.models import Image
    from wagtail_factories import CollectionFactory
    from wagtail.core.models import Collection

    images_path = "fill_media"
    directories = [filename for filename in os.listdir(images_path)]
    for directory in directories:
        collection = Collection.objects.filter(name=directory.capitalize()).first() or \
            CollectionFactory(name=directory.capitalize())
        filenames = [filename for filename in os.listdir(os.path.join(images_path, directory))]

        for filename in filenames:
            full_path = os.path.join(images_path, directory, filename)
            with open(full_path, 'rb') as f:
                image_file = ImageFile(f, name=filename)
                image = Image(file=image_file, title=filename)
                image.collection = collection
                image.save()
        print(f"Loaded {Image.objects.count()} images from {directory}")


def clean():
    from wagtail.images.models import Image
    from home.models import Technology, Responsibility, HomePage
    from wagtail.core.models import Site

    Image.objects.all().delete()
    Technology.objects.all().delete()
    Responsibility.objects.all().delete()
    HomePage.objects.all().delete()
    Site.objects.all().delete()

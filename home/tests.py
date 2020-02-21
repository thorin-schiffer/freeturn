from datetime import timedelta

import pytest
from faker import Faker
from wagtail.core.models import Site

from home.initial_filling import fill_pages
from home.models import Technology, HomePage, ProjectPage, PortfolioPage, TechnologiesPage

fake = Faker()


@pytest.mark.django_db
def test_home(home_page,
              contact_page,
              contact_page_factory,
              project_page,
              rf):
    request = rf.get("/")
    context = home_page.get_context(request)

    form_no_button = contact_page_factory.create(show_on_home=False)

    assert context['forms'][0] == contact_page
    assert form_no_button not in context['forms']
    assert context['current_project'] == project_page
    assert context['earliest_available'] == home_page.earliest_available

    home_page.earliest_available = None

    context = home_page.get_context(request)
    assert context['earliest_available'] == project_page.start_date + timedelta(days=31 * project_page.duration)


@pytest.mark.django_db
def test_portfolio(portfolio_page,
                   project_page_factory,
                   technology,
                   rf):
    project_page = project_page_factory.create(parent=portfolio_page)
    project_page.technologies.add(technology)
    project_page.save()
    request = rf.get(f"/?technology={technology.name}")
    context = portfolio_page.get_context(request)

    assert context['technology'] == technology
    assert project_page in context['projects']


@pytest.mark.django_db
def test_technologies(rf,
                      technology,
                      project_page_factory,
                      technologies_page,
                      portfolio_page):
    request = rf.get("/")
    project_page = project_page_factory.create(parent=portfolio_page)
    context = technologies_page.get_context(request)
    project_page.technologies.add(technology)
    project_page.save()

    assert technology in context['technologies']
    technology = context['technologies'][0]
    assert technology.projects_count == 1
    assert context['portfolio'] == portfolio_page


@pytest.mark.django_db
def test_contact_form_recaptcha(django_app,
                                default_site,
                                portfolio_page,
                                technologies_page,
                                contact_page_factory):
    contact_page = contact_page_factory.create(parent=default_site.root_page)
    r = django_app.get(f"/{contact_page.slug}/", status="*")
    r.form.submit()


@pytest.mark.django_db
def test_match_text(technology):
    # avoid vocabulary collision
    technology.name = "xxx"
    technology.save()

    text_no_match = fake.text()
    assert technology.name not in text_no_match
    text_match = f"{text_no_match} {technology.name}"

    result = Technology.match_text(text_no_match)
    assert technology not in result

    result = Technology.match_text(text_match)
    assert technology in result


@pytest.mark.django_db
def test_fill_pages():
    fill_pages()
    root_page = Site.objects.first().root_page
    home_page = HomePage.objects.child_of(root_page).live().first()
    assert home_page
    assert PortfolioPage.objects.child_of(home_page).live().count() == 1
    assert TechnologiesPage.objects.child_of(home_page).live().count() == 1

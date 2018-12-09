from datetime import timedelta

import pytest
from faker import Faker

from home.models import TechnologyInfo

fake = Faker()


@pytest.mark.django_db
def test_home(home_page,
              contact_page,
              project_page,
              rf):
    request = rf.get("/")
    context = home_page.get_context(request)

    assert context['forms'][0] == contact_page
    assert context['current_project'] == project_page
    assert context['earliest_available'] == home_page.earliest_available

    home_page.earliest_available = None

    context = home_page.get_context(request)
    assert context['earliest_available'] == project_page.start_date + timedelta(days=31 * project_page.duration)


@pytest.mark.django_db
def test_portfolio(portfolio_page,
                   project_page_factory,
                   technology_info,
                   rf):
    project_page = project_page_factory.create(parent=portfolio_page)
    project_page.technologies.add(technology_info.tag)
    project_page.save()
    request = rf.get(f"/?technology={technology_info.tag.name}")
    context = portfolio_page.get_context(request)

    assert context['technology'] == technology_info
    assert project_page in context['projects']


@pytest.mark.django_db
def test_technologies(rf,
                      technology_info,
                      project_page_factory,
                      technologies_page,
                      portfolio_page):
    request = rf.get("/")
    project_page = project_page_factory.create(parent=portfolio_page)
    context = technologies_page.get_context(request)
    project_page.technologies.add(technology_info.tag)
    project_page.save()

    assert technology_info.tag in context['technologies']
    tag = context['technologies'][0]
    assert tag.projects_count == 1
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
def test_match_text(technology_info):
    # avoid vocabulary collision
    technology_info.tag.name = "xxx"
    technology_info.tag.save()

    text_no_match = fake.text()
    assert technology_info.tag.name not in text_no_match
    text_match = f"{text_no_match} {technology_info.tag.name}"

    result = TechnologyInfo.match_text(text_no_match)
    assert technology_info not in result

    result = TechnologyInfo.match_text(text_match)
    assert technology_info in result

from datetime import timedelta

import pytest


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
    assert context['earliest_available'] == project_page.start_date + timedelta(days=31)


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
def test_technologies(rf,
                      portfolio_page,
                      technologies_page,
                      contact_page):
    request = rf.get("/")
    r = contact_page.render_landing_page(request)
    assert r.status_code == 200

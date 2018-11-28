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

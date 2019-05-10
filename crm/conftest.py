import json
import os

import wagtail_factories
from pytest_factoryboy import register
from crm import factories
import pytest

from home.factories import SiteFactory, HomePageFactory, ProjectPageFactory

register(factories.CityFactory)
register(factories.EmployeeFactory)
register(factories.ChannelFactory)
register(factories.CompanyFactory)
register(factories.ProjectFactory)
register(factories.ProjectMessageFactory)
register(factories.UserFactory)
register(factories.AdminFactory, "admin_user")
register(factories.CVFactory)
register(factories.CVWithRelevantFactory, "cv_with_relevant")
register(factories.InvoiceFactory)
register(SiteFactory)
register(HomePageFactory)
register(ProjectPageFactory)
register(wagtail_factories.ImageFactory)
register(wagtail_factories.CollectionFactory)
register(factories.UserSocialAuthFactory)


@pytest.fixture
def admin_app(django_app, admin_user):
    django_app.set_user(admin_user)
    return django_app


@pytest.fixture
def default_site(site_factory):
    return site_factory.create(is_default_site=True)


@pytest.fixture
def gmail_api_response_factory():
    def _gmail_api_response_factory(filename):
        from django.conf import settings
        path = os.path.join(
            settings.BASE_DIR, "crm", "tests", "data", filename
        )
        with open(path, "r") as f:
            return json.load(f)

    return _gmail_api_response_factory

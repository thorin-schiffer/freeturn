import json

import os
import pytest
import wagtail_factories
from pytest_factoryboy import register

from crm import factories
from home.factories import SiteFactory, HomePageFactory, ProjectPageFactory

register(factories.CityFactory)
register(factories.EmployeeFactory)
register(factories.CompanyFactory)
register(factories.ProjectFactory)
register(factories.ProjectMessageFactory)
register(factories.UserFactory)
register(factories.AdminFactory, 'admin_user')
register(factories.CVFactory, include_portfolio=False)
register(factories.MessageTemplateFactory)
register(factories.CVWithRelevantFactory, 'cv_with_relevant')
register(factories.InvoiceFactory)
register(SiteFactory)
register(HomePageFactory)
register(ProjectPageFactory)
register(wagtail_factories.ImageFactory)
register(wagtail_factories.CollectionFactory)
register(factories.UserSocialAuthFactory)


@pytest.fixture
def admin_app(default_locale, django_app, admin_user):
    django_app.set_user(admin_user)
    return django_app


@pytest.fixture
def default_site(default_locale, site_factory):
    return site_factory.create(is_default_site=True)


@pytest.fixture
def gmail_api_response_factory():
    def _gmail_api_response_factory(filename):
        from django.conf import settings
        path = os.path.join(
            settings.BASE_DIR, 'unit_tests', 'crm_tests', 'data', filename
        )
        with open(path, 'r') as f:
            return json.load(f)

    return _gmail_api_response_factory


@pytest.fixture
def gmail_service(mocker, gmail_api_response_factory, monkeypatch, settings):
    monkeypatch.setenv('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY', '111')
    monkeypatch.setenv('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET', '111')
    settings.AUTHENTICATION_BACKENDS = (
        'social_core.backends.google.GoogleOAuth2',
        'django.contrib.auth.backends.ModelBackend',
    )
    settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '111'
    service = mocker.Mock()
    mocker.patch('googleapiclient.discovery.build', return_value=service)
    mocker.patch('crm.gmail_utils.get_labels', lambda s: gmail_api_response_factory('gmapi_labels_response.json'))
    mocker.patch('crm.gmail_utils.get_message_ids',
                 lambda s, l: {'messages': [gmail_api_response_factory('gmail_api_message.json')]})
    mocker.patch('crm.gmail_utils.get_message_raws',
                 lambda s, l: gmail_api_response_factory('gmail_api_message.json'))
    return service

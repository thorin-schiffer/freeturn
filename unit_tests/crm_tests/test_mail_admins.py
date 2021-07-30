import pytest
from django.urls import reverse
from google.auth.exceptions import GoogleAuthError

from crm.factories import UserSocialAuthFactory, ProjectMessageFactory
from crm.models import ProjectMessage


@pytest.mark.django_db
def test_project_message_index(admin_app,
                               project_message,
                               project_message_factory):
    project_message_factory.create()
    url = reverse('crm_projectmessage_modeladmin_index')
    admin_app.get(url)


@pytest.mark.django_db
def test_project_message_index_google_auth_error(admin_app,
                                                 mocker):
    mocker.patch('crm.gmail_utils.sync', side_effect=GoogleAuthError)
    url = reverse('crm_projectmessage_modeladmin_index')
    r = admin_app.get(url)
    assert len(r.context['messages']) == 1
    assert 'Can&#x27;t update messages' in r.text


@pytest.mark.django_db
def test_project_message_index_creates_message(default_site, gmail_service, admin_app, admin_user):
    UserSocialAuthFactory(user=admin_user)
    assert ProjectMessage.objects.count() == 0
    url = reverse('crm_projectmessage_modeladmin_index')
    admin_app.get(url)
    assert ProjectMessage.objects.count() == 1


@pytest.mark.django_db
def test_project_message_inspect(admin_app,
                                 project_message):
    url = reverse('crm_projectmessage_modeladmin_inspect', kwargs={'instance_pk': project_message.pk})
    admin_app.get(url)


@pytest.mark.django_db
def test_project_message_inspect_no_project(admin_app):
    # https://sentry.io/share/issue/5ca8418a573d4ab59df0e1e5c34a1953/
    project_message = ProjectMessageFactory(project=None)
    url = reverse('crm_projectmessage_modeladmin_inspect', kwargs={'instance_pk': project_message.pk})
    admin_app.get(url)

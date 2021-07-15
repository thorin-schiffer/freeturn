import pytest
from django.urls import reverse

from crm.factories import UserSocialAuthFactory
from crm.models import ProjectMessage


@pytest.mark.django_db
def test_project_message_index(admin_app,
                               project_message,
                               project_message_factory):
    project_message_factory.create()
    url = reverse('crm_projectmessage_modeladmin_index')
    admin_app.get(url)


@pytest.mark.django_db
def test_project_message_index_creates_message(gmail_service, admin_app, admin_user):
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

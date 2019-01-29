import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_project_message_index(admin_app,
                               project_message,
                               project_message_factory):
    project_message_factory.create()
    url = reverse('crm_projectmessage_modeladmin_index')
    admin_app.get(url)


@pytest.mark.django_db
def test_project_message_inspect(admin_app,
                                 project_message):
    url = reverse('crm_projectmessage_modeladmin_inspect', kwargs={'instance_pk': project_message.pk})
    admin_app.get(url)

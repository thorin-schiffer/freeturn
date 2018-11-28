import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_index(admin_app,
               project_message,
               project_message_factory):
    project_message_factory.create()
    url = reverse('crm_projectmessage_modeladmin_index')
    r = admin_app.get(url)
    assert r.status_code == 200

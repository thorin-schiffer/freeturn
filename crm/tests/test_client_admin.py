import pytest
from django.urls import reverse

from utils import result_pks, required_inputs


@pytest.mark.django_db
def test_index(admin_app,
               client_company,
               client_company_factory):
    other_client = client_company_factory()
    assert other_client.location != client_company.location
    url = reverse('crm_clientcompany_modeladmin_index')
    r = admin_app.get(url)
    r = r.click(client_company.location.name)
    assert r.status_code == 200
    result = result_pks(r)
    assert client_company.pk in result


@pytest.mark.django_db
def test_add(admin_app):
    url = reverse('crm_clientcompany_modeladmin_create')
    r = admin_app.get(url)
    assert r.status_code == 200
    required = required_inputs(r)
    assert 'name' in required
    assert 'location' in required


def test_delete():
    pytest.fail()


def test_edit():
    pytest.fail()


def test_inspect():
    pytest.fail()

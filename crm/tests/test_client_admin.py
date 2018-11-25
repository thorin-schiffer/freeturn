import pytest
from django.urls import reverse

from utils import result_pks


@pytest.mark.django_db
def test_index(django_app,
               admin_user,
               client_company,
               client_company_factory):
    other_client = client_company_factory()
    assert other_client.location != client_company.location
    url = reverse('crm_clientcompany_modeladmin_index')
    r = django_app.get(url, user=admin_user)
    r = r.click(client_company.location.name)
    assert r.status_code == 200
    result = result_pks(r)
    assert client_company.pk in result


def test_add():
    pytest.fail()


def test_delete():
    pytest.fail()


def test_edit():
    pytest.fail()


def test_inspect():
    pytest.fail()

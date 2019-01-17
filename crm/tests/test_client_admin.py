import pytest
from django.urls import reverse

from crm.models import ClientCompany
from utils import result_pks, required_inputs
from faker import Faker

fake = Faker()


@pytest.mark.django_db
def test_index(admin_app,
               client_company,
               client_company_factory):
    other_client = client_company_factory()
    assert other_client.location != client_company.location
    url = reverse('crm_clientcompany_modeladmin_index')
    r = admin_app.get(url)
    r = r.click(client_company.location.name)
    result = result_pks(r)
    assert client_company.pk in result


@pytest.mark.django_db
def test_add_required(admin_app):
    url = reverse('crm_clientcompany_modeladmin_create')
    r = admin_app.get(url)
    required = required_inputs(r)
    assert 'name' in required


@pytest.mark.django_db
def test_add(admin_app,
             city, channel):
    url = reverse('crm_clientcompany_modeladmin_create')
    r = admin_app.get(url)
    form = r.forms[1]
    assert form.action == url
    name = fake.sentence()
    form['name'] = name
    form['location'] = city.id
    form['channel'] = channel.id
    form['url'] = fake.uri()
    form['notes'] = fake.text()

    r = form.submit().follow()
    assert ClientCompany.objects.filter(name=name).exists()


@pytest.mark.django_db
def test_delete(admin_app,
                client_company):
    url = reverse('crm_clientcompany_modeladmin_delete', kwargs={'instance_pk': client_company.pk})
    r = admin_app.get(url)
    form = r.forms[1]
    assert form.action == url

    form.submit()
    assert not ClientCompany.objects.filter(pk=client_company.pk).exists()


@pytest.mark.django_db
def test_inspect(admin_app,
                 client_company):
    url = reverse('crm_clientcompany_modeladmin_inspect', kwargs={'instance_pk': client_company.pk})
    admin_app.get(url)

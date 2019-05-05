import pytest
from django.urls import reverse

from crm.models import Company
from utils import result_pks, required_inputs
from faker import Faker

fake = Faker()


@pytest.mark.django_db
def test_index(admin_app,
               company,
               company_factory):
    other_client = company_factory()
    assert other_client.location != company.location
    url = reverse('crm_company_modeladmin_index')
    r = admin_app.get(url)
    r = r.click(company.location.name)
    result = result_pks(r)
    assert company.pk in result


@pytest.mark.django_db
def test_add_required(admin_app):
    url = reverse('crm_company_modeladmin_create')
    r = admin_app.get(url)
    required = required_inputs(r)
    assert 'name' in required


@pytest.mark.django_db
def test_add(admin_app,
             city, channel):
    url = reverse('crm_company_modeladmin_create')
    r = admin_app.get(url)
    form = r.forms[1]
    assert form.action == url
    name = fake.sentence()
    form['name'] = name
    form['location'] = city.id
    form['channel'] = channel.id
    form['url'] = fake.uri()
    form['notes'] = fake.text()

    form.submit().follow()
    assert Company.objects.filter(name=name).exists()


@pytest.mark.django_db
def test_delete(admin_app,
                company):
    url = reverse('crm_company_modeladmin_delete', kwargs={'instance_pk': company.pk})
    r = admin_app.get(url)
    form = r.forms[1]
    assert form.action == url

    form.submit()
    assert not Company.objects.filter(pk=company.pk).exists()


@pytest.mark.django_db
def test_inspect(admin_app,
                 company):
    url = reverse('crm_company_modeladmin_inspect', kwargs={'instance_pk': company.pk})
    admin_app.get(url)

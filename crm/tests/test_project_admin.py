from datetime import datetime

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_index_action(admin_app,
                      project):
    assert project.state == 'requested'
    url = reverse('crm_project_modeladmin_index')
    r = admin_app.get(url)
    r = r.click("Drop")
    inputs = r.lxml.xpath(".//*[@id='id_notes']")
    assert len(inputs) == 1

    r = r.forms[1].submit().follow()

    project.refresh_from_db()
    assert project.state == 'stopped'
    assert len(r.context['messages']) == 1


@pytest.mark.django_db
def test_inspect(admin_app,
                 project):
    url = reverse('crm_project_modeladmin_inspect', kwargs={'instance_pk': project.pk})
    admin_app.get(url)


@pytest.mark.django_db
def test_inspect_blank(admin_app, project_factory):
    project = project_factory.create(
        project_page=None,
        start_date=None,
        end_date=None,
        daily_rate=None
    )
    url = reverse('crm_project_modeladmin_inspect', kwargs={'instance_pk': project.pk})
    admin_app.get(url)


@pytest.mark.django_db
def test_create_redirect_to_cv_creation(admin_app,
                                        city,
                                        default_site):
    project_create_url = reverse('crm_project_modeladmin_create')
    r = admin_app.get(project_create_url)
    form = r.forms[1]
    form['location'] = str(city.pk)
    r = r.forms[1].submit()
    cv_create_url = reverse('crm_cv_modeladmin_create')
    assert cv_create_url in r.location
    r = r.follow()
    assert len(r.context['messages']) == 2


@pytest.mark.django_db
def test_create_dates_prefill(admin_app,
                              mocker):
    date = datetime(2019, 1, 24)
    mocker.patch('django.utils.timezone.now',
                 side_effect=lambda *args: date)
    project_create_url = reverse('crm_project_modeladmin_create')
    r = admin_app.get(project_create_url)
    form = r.forms[1]

    assert form['start_date'].value == '2019-02-01'
    assert form['end_date'].value == '2019-05-01'

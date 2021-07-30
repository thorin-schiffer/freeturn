from datetime import datetime

import pytest
from django.contrib.messages import ERROR
from django.urls import reverse
from google.api_core.exceptions import GoogleAPIError

from crm.factories import CityFactory, ProjectFactory, MessageTemplateFactory, CVFactory, UserSocialAuthFactory
from utils import get_messages


@pytest.mark.django_db
def test_state_transition_action(gmail_service,
                                 admin_app,
                                 admin_user,
                                 project):
    UserSocialAuthFactory(user=admin_user)
    MessageTemplateFactory(state_transition='drop')
    CVFactory(project=project)
    assert project.state == 'requested'
    url = reverse('crm_project_modeladmin_index')
    r = admin_app.get(url)
    r = r.click('Drop')
    drop_state_url = reverse('crm_project_modeladmin_state',
                             kwargs={
                                 'instance_pk': project.pk,
                                 'action': 'drop'
                             })
    assert r.request.path == drop_state_url
    form = r.forms[1]
    assert 'template' in form.fields
    assert 'text' not in form.fields
    assert 'cv' not in form.fields
    r = form.submit(name='next')

    form = r.forms[1]
    assert 'text' in form.fields
    assert 'cv' in form.fields
    r = form.submit(name='send').follow()
    project.refresh_from_db()
    assert project.state == 'stopped'
    assert len(r.context['messages']) == 2


@pytest.mark.django_db
def test_state_transition_no_social_auth(gmail_service,
                                         admin_app,
                                         project):
    MessageTemplateFactory(state_transition='drop')
    CVFactory(project=project)
    assert project.state == 'requested'
    url = reverse('crm_project_modeladmin_index')
    r = admin_app.get(url)
    r = r.click('Drop')
    assert len(r.context['messages']) == 1
    r = r.forms[1].submit().follow()
    assert len(r.context['messages']) == 1


@pytest.mark.django_db
def test_state_transition_no_manager_associated(gmail_service,
                                                admin_user,
                                                admin_app):
    # https://sentry.io/share/issue/2f073f4072824a82bade78c6472e1faf/
    project = ProjectFactory(manager=None)
    UserSocialAuthFactory(user=admin_user)

    MessageTemplateFactory(state_transition='drop')
    CVFactory(project=project)
    url = reverse('crm_project_modeladmin_index')
    r = admin_app.get(url)
    r = r.click('Drop')
    r = r.forms[1].submit(name='next')
    messages = get_messages(r)
    assert len(messages) == 1
    assert messages[0][0] == 'error'
    assert messages[0][1] == "Project doesn't have a manager, messages can't be sent"
    assert r.lxml.xpath(".//button[@value='change_state']")
    assert not r.lxml.xpath(".//button[@value='Send']")


@pytest.mark.django_db
def test_state_transition_just_change_state_button(gmail_service,
                                                   admin_app,
                                                   project):
    MessageTemplateFactory(state_transition='drop')
    CVFactory(project=project)
    assert project.state == 'requested'
    url = reverse('crm_project_modeladmin_index')
    r = admin_app.get(url)
    r = r.click('Drop')
    r = r.forms[1].submit(name='change_state', value='Just change state').follow()
    project.refresh_from_db()
    assert project.state == 'stopped'
    assert len(r.context['messages']) == 1


@pytest.mark.django_db
def test_state_transition_google_api_error(gmail_service,
                                           admin_app,
                                           project,
                                           mocker):
    mocker.patch('crm.gmail_utils.send_email', side_effect=GoogleAPIError)
    MessageTemplateFactory(state_transition='drop')
    CVFactory(project=project)
    assert project.state == 'requested'
    url = reverse('crm_project_modeladmin_index')
    r = admin_app.get(url)
    r = r.click('Drop')
    r = r.forms[1].submit(name='change_state', value='Just change state').follow()
    project.refresh_from_db()
    assert project.state == 'stopped'
    assert r.context['messages']._get()[0][0].level == ERROR


@pytest.mark.django_db
def test_inspect(admin_app,
                 project_factory,
                 project_page):
    project = project_factory.create(project_page=project_page)
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
    form['name'] = 'test name'
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


@pytest.mark.django_db
def test_create_location_prefill(admin_app, city):
    most_frequent_city = CityFactory()
    ProjectFactory(location=most_frequent_city)
    ProjectFactory(location=most_frequent_city)
    assert city.project_count < most_frequent_city.project_count
    project_create_url = reverse('crm_project_modeladmin_create')
    r = admin_app.get(project_create_url)
    form = r.forms[1]

    assert form['location'].value == str(most_frequent_city.pk)

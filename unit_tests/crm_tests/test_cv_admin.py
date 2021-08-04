import pytest
from django.urls import reverse

from crm.models.settings import CVGenerationSettings
from home.factories import ProjectPageFactory, PortfolioPageFactory


@pytest.mark.django_db
def test_create(admin_app, admin_user, default_site, project, image):
    # cv creation form prefilled with settings from cv generator settings
    cv_settings = CVGenerationSettings.for_site(default_site)
    cv_settings.default_picture = image
    cv_settings.save()
    url = f"{reverse('crm_cv_modeladmin_create')}?for_project={project.pk}"

    r = admin_app.get(url)
    form = r.forms[1]

    assert cv_settings.default_title in form['title'].value
    assert cv_settings.default_experience_overview in form['experience_overview'].value
    assert cv_settings.default_education_overview in form['education_overview'].value
    assert cv_settings.default_contact_details in form['contact_details'].value
    assert cv_settings.default_languages_overview in form['languages_overview'].value
    assert cv_settings.default_rate_overview in form['rate_overview'].value
    assert cv_settings.default_working_permit in form['working_permit'].value
    assert (admin_user.first_name + ' ' + admin_user.last_name) in form['full_name'].value
    assert str(cv_settings.default_picture.id) in form['picture'].value
    assert str(project.id) in form['project'].value
    form.submit()


@pytest.mark.django_db
def test_inspect(admin_app, cv_with_relevant):
    PortfolioPageFactory()
    cv_with_relevant.relevant_project_pages.add(ProjectPageFactory())
    url = reverse('crm_cv_modeladmin_inspect', kwargs={'instance_pk': cv_with_relevant.pk})
    r = admin_app.get(url)
    relevant_pages = r.context['relevant_project_pages']
    assert relevant_pages[0] == cv_with_relevant.highlighted_project_pages.first()


@pytest.mark.django_db
def test_create_empty_project(admin_app, admin_user, default_site):
    url = f"{reverse('crm_cv_modeladmin_create')}"
    r = admin_app.get(url)
    form = r.forms[1]
    assert form.submit().maybe_follow().status_code == 200

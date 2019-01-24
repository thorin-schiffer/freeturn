import pytest
from django.urls import reverse

from crm.models import CVGenerationSettings


@pytest.mark.django_db
def test_create(admin_app, admin_user, default_site, project, image):
    # cv creation form prefilled with settings from cv generator settings
    cv_settings = CVGenerationSettings.for_site(default_site)
    cv_settings.default_picture = image
    cv_settings.save()
    url = reverse('crm_cv_modeladmin_create')

    r = admin_app.get(url)
    form = r.forms[1]
    assert form.action == url

    assert form['title'].value == cv_settings.default_title
    assert form['experience_overview'].value == cv_settings.default_experience_overview
    assert form['education_overview'].value == cv_settings.default_education_overview
    assert form['contact_details'].value == cv_settings.default_contact_details
    assert form['languages_overview'].value == cv_settings.default_languages_overview
    assert form['rate_overview'].value == cv_settings.default_rate_overview
    assert form['working_permit'].value == cv_settings.default_working_permit
    assert form['full_name'].value == admin_user.first_name + " " + admin_user.last_name
    assert form['picture'].value == str(cv_settings.default_picture.id)
    form['project'] = str(project.id)
    form.submit()


@pytest.mark.django_db
def test_inspect(admin_app, cv_with_relevant):
    url = reverse('crm_cv_modeladmin_inspect', kwargs={'instance_pk': cv_with_relevant.pk})
    admin_app.get(url)

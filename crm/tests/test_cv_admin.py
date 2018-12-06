import pytest
from django.urls import reverse

from crm.models import CVGenerationSettings


@pytest.mark.django_db
def test_add_form_prefill(admin_app, default_site):
    # cv creation form prefilled with settings from cv generator settings
    cv_settings = CVGenerationSettings.for_site(default_site)
    url = reverse('crm_cv_modeladmin_create')

    r = admin_app.get(url)
    form = r.forms[1]
    assert form.action == url

    assert form['title'] == cv_settings.default_title
    assert form['experience_overview'] == cv_settings.default_experience_overview
    assert form['education_overview'] == cv_settings.default_education_overview
    assert form['contact_details'] == cv_settings.default_contact_details
    assert form['languages_overview'] == cv_settings.default_languages_overview
    assert form['rate_overview'] == cv_settings.default_rate_overview

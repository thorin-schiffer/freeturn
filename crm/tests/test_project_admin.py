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
    assert r.status_code == 200

    project.refresh_from_db()
    assert project.state == 'stopped'
    assert len(r.context['messages']) == 1

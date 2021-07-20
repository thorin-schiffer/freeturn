from django.urls import reverse
from wagtail.tests.utils.form_data import rich_text
import pytest

from crm.models import MessageTemplate


@pytest.mark.django_db
def test_save_template(admin_app):
    url = reverse('crm_messagetemplate_modeladmin_create')
    r = admin_app.get(url)
    form = r.forms[1]
    form['text'] = rich_text('{{project.name}}')
    form['state_transition'] = 'scope'
    form['name'] = 'name'
    form.submit()
    assert MessageTemplate.objects.filter(name='name').exists()


@pytest.mark.django_db
def test_save_template_invalid_syntax(admin_app):
    url = reverse('crm_messagetemplate_modeladmin_create')
    r = admin_app.get(url)
    form = r.forms[1]
    form['text'] = rich_text('{% if %}')
    form['state_transition'] = 'scope'
    form['name'] = 'name'
    form.submit()
    assert not MessageTemplate.objects.filter(name='name').exists()

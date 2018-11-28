import pytest
from django.urls import reverse

from crm.wagtail_admin.mail import MailboxButtonHelper, MailboxAdmin


@pytest.mark.django_db
def test_index(admin_app,
               project_message,
               project_message_factory):
    project_message_factory.create()
    url = reverse('crm_projectmessage_modeladmin_index')
    r = admin_app.get(url)
    assert r.status_code == 200


@pytest.fixture
def button_helper(rf, admin_user):
    request = rf.get(reverse('crm_mailbox_modeladmin_index'))
    request.user = admin_user
    model_admin = MailboxAdmin()
    view = model_admin.index_view_class(model_admin=model_admin)
    return MailboxButtonHelper(
        request=request,
        view=view
    )


@pytest.mark.django_db
def test_get_mail_button(project_message, button_helper):
    buttons = button_helper.get_buttons_for_obj(project_message)
    get_mail_button = next(button for button in buttons if button['label'] == 'Get mail')
    assert get_mail_button
    assert get_mail_button['url'] == reverse(
        'crm_mailbox_modeladmin_get_mail', kwargs={
            'instance_pk': project_message.pk
        }
    )

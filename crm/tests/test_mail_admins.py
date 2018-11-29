import pytest
from django.contrib.messages import SUCCESS, WARNING
from django.urls import reverse

from crm.wagtail_admin.mail import MailboxButtonHelper, MailboxAdmin


@pytest.mark.django_db
def test_project_message_index(admin_app,
                               project_message,
                               project_message_factory):
    project_message_factory.create()
    url = reverse('crm_projectmessage_modeladmin_index')
    r = admin_app.get(url)


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
def test_get_mail_button(mailbox, button_helper):
    buttons = button_helper.get_buttons_for_obj(mailbox)
    get_mail_button = next(button for button in buttons if button['label'] == 'Get mail')
    assert get_mail_button
    assert get_mail_button['url'] == reverse(
        'crm_mailbox_modeladmin_get_mail', kwargs={
            'instance_pk': mailbox.pk
        }
    )


@pytest.mark.django_db
def test_get_mail_view_no_mail(admin_app,
                               mailbox,
                               mocker):
    mocker.patch('crm.models.Mailbox.get_new_mail', side_effect=lambda: [])
    url = reverse(
        'crm_mailbox_modeladmin_get_mail', kwargs={
            'instance_pk': mailbox.pk
        }
    )
    r = admin_app.get(url).follow()
    messages = r.context['messages']
    assert len(messages) == 1
    message = messages._loaded_messages[0]
    assert message.level == WARNING


@pytest.mark.django_db
def test_get_mail_view_new_mail(admin_app,
                                mailbox,
                                mocker):
    mocker.patch('crm.models.Mailbox.get_new_mail', side_effect=lambda: ["foo"])
    url = reverse(
        'crm_mailbox_modeladmin_get_mail', kwargs={
            'instance_pk': mailbox.pk
        }
    )
    r = admin_app.get(url).follow()

    assert len(r.context['messages']) == 1
    messages = r.context['messages']
    message = messages._loaded_messages[0]
    assert message.level == SUCCESS


@pytest.mark.django_db
def test_project_message_inspect(admin_app,
                                 project_message):
    url = reverse('crm_projectmessage_modeladmin_inspect', kwargs={'instance_pk': project_message.pk})
    r = admin_app.get(url)

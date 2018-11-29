from django.conf.urls import url
from django.contrib.admin.utils import quote
from django.contrib.auth.models import Permission
from django.shortcuts import redirect
from wagtail.admin import messages
from wagtail.contrib.modeladmin.helpers import ButtonHelper, PermissionHelper
from wagtail.contrib.modeladmin.options import ModelAdmin, ModelAdminGroup
from wagtail.contrib.modeladmin.views import InstanceSpecificView

from crm.models import ProjectMessage, Mailbox


class MessageAdmin(ModelAdmin):
    model = ProjectMessage
    menu_icon = 'fa-envelope-open'
    menu_label = 'Messages'
    list_display = ['subject', 'author', 'project', 'created']
    list_filter = ['project', 'author']
    ordering = ['-created']
    inspect_view_enabled = True
    inspect_view_fields = ['project', 'subject', 'from_address', 'text']


class GetMailView(InstanceSpecificView):
    action = 'get_mail'
    page_title = 'Get mail'

    def get(self, *args, **kwargs):
        new_mails = self.instance.get_new_mail()
        if new_mails:
            messages.success(
                self.request, f"Mail updated for {self.instance}: {len(new_mails)} new mails"
            )
        else:
            messages.warning(
                self.request, f"Mail updated for {self.instance}: no new mails"
            )
        return redirect(self.index_url)


class MailboxButtonHelper(ButtonHelper):
    def get_mail(self, obj, pk):
        return {
            'url': self.url_helper.get_action_url('get_mail', quote(pk)),
            'label': "Get mail",
            'classname': self.finalise_classname(['button-small']),
            'title': "Get last mails from server",
        }

    def get_buttons_for_obj(self, obj, *args, **kwargs):
        btns = super().get_buttons_for_obj(obj, *args, **kwargs)
        usr = self.request.user
        ph = self.permission_helper
        pk = getattr(obj, self.opts.pk.attname)

        if ph.user_can_edit_obj(usr, obj):
            btns.append(self.get_mail(obj, pk))
        return btns


class MailboxPermissionHelper(PermissionHelper):
    def get_all_model_permissions(self):
        return Permission.objects.filter(
            content_type__app_label='django_mailbox',
            content_type__model='mailbox',
        )


class MailboxAdmin(ModelAdmin):
    model = Mailbox
    menu_icon = 'fa-address-card'
    button_helper_class = MailboxButtonHelper
    permission_helper_class = MailboxPermissionHelper

    def get_mail_view(self, request, instance_pk):
        kwargs = {'model_admin': self, 'instance_pk': instance_pk}
        return GetMailView.as_view(**kwargs)(request)

    def get_admin_urls_for_registration(self):
        urls = super().get_admin_urls_for_registration()
        route = url(self.url_helper.get_action_url_pattern('get_mail'),
                    self.get_mail_view,
                    name=self.url_helper.get_action_url_name('get_mail'))
        urls = urls + (route,)
        return urls


class MailGroup(ModelAdminGroup):
    menu_label = "Mail"
    menu_icon = "fa-envelope"
    menu_order = 200
    items = (
        MessageAdmin, MailboxAdmin
    )

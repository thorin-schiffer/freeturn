from wagtail.contrib.modeladmin.options import ModelAdmin, ModelAdminGroup

from crm.models import ProjectMessage


class MessageAdmin(ModelAdmin):
    model = ProjectMessage
    menu_icon = 'fa-envelope-open'
    menu_label = 'Messages'
    list_display = ['subject', 'author', 'project', 'created']
    list_filter = ['project', 'author']
    ordering = ['-created']
    inspect_view_enabled = True
    inspect_view_fields = ['project', 'subject', 'from_address', 'text']


class MailGroup(ModelAdminGroup):
    menu_label = "Mail"
    menu_icon = "fa-envelope"
    menu_order = 200
    items = (
        MessageAdmin
    )

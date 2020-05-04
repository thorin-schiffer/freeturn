from instance_selector.registry import registry
from instance_selector.selectors import ModelAdminInstanceSelector
from wagtail.contrib.modeladmin.mixins import ThumbnailMixin
from wagtail.contrib.modeladmin.options import ModelAdmin

from crm.models import Employee


class EmployeeAdmin(ThumbnailMixin, ModelAdmin):
    model = Employee
    menu_icon = 'fa-users'
    menu_label = 'People'
    search_fields = ('telephone', 'first_name', 'last_name', 'company__name', 'email', 'mobile')
    list_display = ('admin_thumb', 'first_name', 'last_name', 'company', 'project_count')
    thumb_image_field_name = 'picture'
    thumb_default = '/static/img/default_avatar.png'


class EmployeeSelector(ModelAdminInstanceSelector):
    model_admin = EmployeeAdmin()

    def get_instance_display_image_url(self, instance):
        if instance and instance.picture:
            return instance.picture.file.url


registry.register_instance_selector(Employee, EmployeeSelector())

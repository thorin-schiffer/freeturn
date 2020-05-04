from instance_selector.registry import registry
from instance_selector.selectors import ModelAdminInstanceSelector
from wagtail.contrib.modeladmin.mixins import ThumbnailMixin
from wagtail.contrib.modeladmin.options import ModelAdmin

from crm.models import Company


class CompanyAdmin(ThumbnailMixin, ModelAdmin):
    model = Company
    menu_label = 'Companies'  # ditch this to use verbose_name_plural from model
    menu_icon = 'fa-building'  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = False  # or True to exclude pages of this type from Wagtail's explorer view
    list_display = ('admin_thumb', 'name', 'location')
    list_filter = ('location', 'channel',)
    search_fields = ('name',)
    thumb_image_field_name = 'logo'
    thumb_default = '/static/img/default_company.png'


class CompanySelector(ModelAdminInstanceSelector):
    model_admin = CompanyAdmin()

    def get_instance_display_image_url(self, instance):
        if instance and instance.logo:
            return instance.logo.file.url


registry.register_instance_selector(Company, CompanySelector())

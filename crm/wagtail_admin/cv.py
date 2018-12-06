from wagtail.contrib.modeladmin.options import ModelAdmin

from crm.models import CV


class CVAdmin(ModelAdmin):
    model = CV
    menu_icon = 'fa-id-card'
    menu_label = 'CVs'

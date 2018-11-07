from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register, ModelAdminGroup)

from crm.models import Company, City, Channel, Project, Employee


class CityAdmin(ModelAdmin):
    model = City
    menu_icon = 'fa-location-arrow'
    menu_label = 'Cities'
    list_display = ('name', 'project_count')


class ChannelAdmin(ModelAdmin):
    model = Channel
    menu_icon = 'fa-arrow-circle-up'
    menu_label = 'Channels'


class ProjectAdmin(ModelAdmin):
    model = Project
    menu_icon = 'fa-product-hunt'
    menu_label = 'Projects'
    list_display = ('company', 'location', 'daily_rate')
    search_fields = ('project_page__title',)


class EmployeeAdmin(ModelAdmin):
    model = Employee
    menu_icon = 'fa-users'
    menu_label = 'People'
    search_fields = ('first_name', 'last_name', 'company__name', 'email')
    list_display = ('first_name', 'last_name', 'company', 'project_count')


class CompanyAdmin(ModelAdmin):
    model = Company
    menu_label = 'Companies'  # ditch this to use verbose_name_plural from model
    menu_icon = 'fa-building'  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = False  # or True to exclude pages of this type from Wagtail's explorer view
    list_display = ('name', 'location', 'channel')
    list_filter = ('location', 'channel',)
    search_fields = ('name',)
    inspect_view_enabled = True
    inspect_view_fields = ['name']


class CRMGroup(ModelAdminGroup):
    menu_label = "CRM"
    menu_icon = "fa-briefcase"
    menu_order = 200
    items = (
        ProjectAdmin, EmployeeAdmin, CompanyAdmin, CityAdmin, ChannelAdmin
    )


# Now you just need to register your customised ModelAdmin class with Wagtail
modeladmin_register(CRMGroup)

from django.urls import reverse
from social_django.models import UserSocialAuth
from wagtail.admin.search import SearchArea
from wagtail.contrib.modeladmin.mixins import ThumbnailMixin
from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register, ModelAdminGroup)
from wagtail.core import hooks

from crm.models import Company, City, Channel, Employee
from crm.wagtail_admin.cv import CVAdmin
from crm.wagtail_admin.invoice import InvoiceAdmin
from crm.wagtail_admin.project import ProjectAdmin, ProjectSearchArea, MessageAdmin


class CityAdmin(ModelAdmin):
    model = City
    menu_icon = 'fa-location-arrow'
    menu_label = 'Cities'
    list_display = ('name', 'project_count')


class ChannelAdmin(ModelAdmin):
    model = Channel
    menu_icon = 'fa-arrow-circle-up'
    menu_label = 'Channels'


class EmployeeAdmin(ThumbnailMixin, ModelAdmin):
    model = Employee
    menu_icon = 'fa-users'
    menu_label = 'People'
    search_fields = ('telephone', 'first_name', 'last_name', 'company__name', 'email', 'mobile')
    list_display = ('admin_thumb', 'first_name', 'last_name', 'company', 'project_count')
    thumb_image_field_name = 'picture'
    thumb_default = '/static/img/default_avatar.png'


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
    inspect_view_enabled = True
    inspect_view_fields = ['name']
    thumb_image_field_name = 'logo'
    thumb_default = '/static/img/default_company.png'


class CRMGroup(ModelAdminGroup):
    menu_label = 'CRM'
    menu_icon = 'fa-briefcase'
    menu_order = 200
    items = (
        ProjectAdmin, CVAdmin, EmployeeAdmin, CompanyAdmin,
        CityAdmin, ChannelAdmin, MessageAdmin,
        InvoiceAdmin
    )


modeladmin_register(CRMGroup)


class PeopleSearchArea(SearchArea):
    def __init__(self):
        super().__init__(
            'People', reverse('crm_employee_modeladmin_index'),
            name='people',
            classnames='icon icon-fa-users',
            order=100)


@hooks.register('register_admin_search_area')
def register_people_search_area():
    return PeopleSearchArea()


@hooks.register('register_admin_search_area')
def register_project_search_area():
    return ProjectSearchArea()


class CompanySearchArea(SearchArea):
    def __init__(self):
        super().__init__(
            'Companies', reverse('crm_company_modeladmin_index'),
            name='companies',
            classnames='icon icon-fa-building',
            order=102)


@hooks.register('register_admin_search_area')
def register_pages_search_area():
    return CompanySearchArea()


@hooks.register('register_account_menu_item')
def google_login(request):
    existing_google_account = UserSocialAuth.objects.filter(user=request.user).first()
    hint = 'Associate google account' if not existing_google_account \
        else f'Logged in with: {existing_google_account.uid}'
    return {
        'url': reverse('social:begin', args=('google-oauth2',)),
        'label': 'Google login',
        'help_text': hint
    }

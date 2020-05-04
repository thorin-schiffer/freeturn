from django.urls import reverse
from social_django.models import UserSocialAuth
from wagtail.admin.search import SearchArea
from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register, ModelAdminGroup)
from wagtail.core import hooks

from crm.models.channel import Channel
from crm.models.city import City
from crm.wagtail_admin.company import CompanyAdmin
from crm.wagtail_admin.cv import CVAdmin
from crm.wagtail_admin.employee import EmployeeAdmin
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

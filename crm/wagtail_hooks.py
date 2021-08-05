from django.db.models import Count
from django.urls import reverse
from social_django.models import UserSocialAuth
from wagtail.admin.search import SearchArea
from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register, ModelAdminGroup)
from wagtail.core import hooks

from crm.models import MessageTemplate
from crm.models.city import City
from crm.wagtail_admin.company import CompanyAdmin
from crm.wagtail_admin.cv import CVAdmin
from crm.wagtail_admin.employee import EmployeeAdmin
from crm.wagtail_admin.invoice import InvoiceAdmin
from crm.wagtail_admin.project import ProjectAdmin, ProjectSearchArea
from crm.wagtail_admin.project_message import MessageAdmin


class CityAdmin(ModelAdmin):
    model = City
    menu_icon = 'fa-location-arrow'
    menu_label = 'Cities'
    list_display = ('name', 'project_count')
    add_to_settings_menu = True

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(c=Count('projects')).order_by('-c')


modeladmin_register(CityAdmin)


class CRMGroup(ModelAdminGroup):
    menu_label = 'CRM'
    menu_icon = 'fa-briefcase'
    menu_order = 200
    items = (
        ProjectAdmin, CVAdmin, CompanyAdmin,
        MessageAdmin, InvoiceAdmin,
        EmployeeAdmin,
    )


modeladmin_register(CRMGroup)


class MessageTemplateAdmin(ModelAdmin):
    model = MessageTemplate
    menu_icon = 'fa-envelope-square'
    menu_label = 'Message templates'
    list_display = ['name', 'state_transition', 'language']
    add_to_settings_menu = True
    list_filter = ['language']


modeladmin_register(MessageTemplateAdmin)


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

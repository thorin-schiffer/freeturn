from django.urls import reverse
from social_django.models import UserSocialAuth
from wagtail.admin.search import SearchArea
from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register, ModelAdminGroup)
from wagtail.core import hooks

from crm.models import Recruiter, City, Channel, Employee, ClientCompany
from crm.wagtail_admin.mail import MailGroup
from crm.wagtail_admin.project import ProjectAdmin, ProjectSearchArea


class CityAdmin(ModelAdmin):
    model = City
    menu_icon = 'fa-location-arrow'
    menu_label = 'Cities'
    list_display = ('name', 'project_count')


class ChannelAdmin(ModelAdmin):
    model = Channel
    menu_icon = 'fa-arrow-circle-up'
    menu_label = 'Channels'


class EmployeeAdmin(ModelAdmin):
    model = Employee
    menu_icon = 'fa-users'
    menu_label = 'People'
    search_fields = ('telephone', 'first_name', 'last_name', 'company__name', 'email', 'mobile')
    list_display = ('first_name', 'last_name', 'company', 'project_count', 'telephone')


class RecruiterAdmin(ModelAdmin):
    model = Recruiter
    menu_label = 'Recruiters'  # ditch this to use verbose_name_plural from model
    menu_icon = 'fa-building'  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = False  # or True to exclude pages of this type from Wagtail's explorer view
    list_display = ('name', 'location', 'channel')
    list_filter = ('location', 'channel',)
    search_fields = ('name',)
    inspect_view_enabled = True
    inspect_view_fields = ['name']


class ClientCompanyAdmin(ModelAdmin):
    model = ClientCompany
    menu_label = 'Clients'
    menu_icon = 'fa-user-circle'
    list_display = ('name', 'location', 'channel')
    list_filter = ('location', 'channel',)
    search_fields = ('name',)
    inspect_view_enabled = True


class CRMGroup(ModelAdminGroup):
    menu_label = "CRM"
    menu_icon = "fa-briefcase"
    menu_order = 200
    items = (
        ProjectAdmin, EmployeeAdmin, RecruiterAdmin, CityAdmin, ChannelAdmin, ClientCompanyAdmin
    )


modeladmin_register(CRMGroup)

modeladmin_register(MailGroup)


class PeopleSearchArea(SearchArea):
    def __init__(self):
        super().__init__(
            "People", reverse('crm_employee_modeladmin_index'),
            name='people',
            classnames='icon icon-fa-users',
            order=100)


@hooks.register('register_admin_search_area')
def register_pages_search_area():
    return PeopleSearchArea()


@hooks.register('register_admin_search_area')
def register_pages_search_area():
    return ProjectSearchArea()


class RecruiterSearchArea(SearchArea):
    def __init__(self):
        super().__init__(
            "Recruiters", reverse('crm_recruiter_modeladmin_index'),
            name='recruiters',
            classnames='icon icon-fa-building',
            order=102)


@hooks.register('register_admin_search_area')
def register_pages_search_area():
    return RecruiterSearchArea()


@hooks.register('register_account_menu_item')
def google_login(request):
    existing_google_account = UserSocialAuth.objects.filter(user=request.user).first()
    hint = "Associate google account" if not existing_google_account \
        else f"Logged in with: {existing_google_account.uid}"
    return {
        'url': reverse('social:begin', args=("google-oauth2",)),
        'label': "Google login",
        'help_text': hint
    }

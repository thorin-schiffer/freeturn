from django.conf.urls import url
from django.contrib.admin.utils import quote
from django.http import Http404
from django.urls import reverse
from django_fsm import TransitionNotAllowed
from wagtail.admin.search import SearchArea
from wagtail.contrib.modeladmin.helpers import ButtonHelper, AdminURLHelper
from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register, ModelAdminGroup)
from wagtail.contrib.modeladmin.views import EditView
from wagtail.core import hooks

from crm.models import Recruiter, City, Channel, Project, Employee, ClientCompany


class CityAdmin(ModelAdmin):
    model = City
    menu_icon = 'fa-location-arrow'
    menu_label = 'Cities'
    list_display = ('name', 'project_count')


class ChannelAdmin(ModelAdmin):
    model = Channel
    menu_icon = 'fa-arrow-circle-up'
    menu_label = 'Channels'


class ProjectURLHelper(AdminURLHelper):
    def get_action_url_pattern(self, action):
        if action == 'state':
            return r'^%s/%s/%s/(?P<instance_pk>[-\w]+)/(?P<action>[-\w]+)/$' % (
                self.opts.app_label, self.opts.model_name, action
            )
        pattern = super().get_action_url_pattern(action)
        return pattern


class StateTransitionView(EditView):
    action = None

    def __init__(self, **kwargs):
        self.action = kwargs.pop('action')
        self.page_title = f"{self.action.capitalize()} {Project._meta.verbose_name}"
        super().__init__(**kwargs)

    def edit_url(self):
        return self.url_helper.get_action_url('state', self.pk_quoted, self.action)

    def get_success_message(self, instance):
        return "{model_name} '{instance}' now in state {instance.state}".format(
            model_name=self.verbose_name.capitalize(), instance=instance
        )

    def form_valid(self, form):
        method = getattr(form.instance, self.action)
        try:
            method()
        except TransitionNotAllowed:
            return self.form_invalid(form)
        return super().form_valid(form)


class ProjectButtonHelper(ButtonHelper):
    def state_buttons(self, obj, pk):
        available_transitions = obj.get_available_state_transitions()
        buttons = []
        for transition in available_transitions:
            action = transition.method.__name__
            buttons.append(
                {
                    'url': self.url_helper.get_action_url('state', quote(pk), action),
                    'label': action.capitalize(),
                    'classname': self.finalise_classname(['button-small'] +
                                                         transition.custom.get('classes', [])),
                    'title': transition.custom['help'].capitalize(),
                }
            )
        return buttons

    def get_buttons_for_obj(self, obj, *args, **kwargs):
        btns = super().get_buttons_for_obj(obj, *args, **kwargs)
        usr = self.request.user
        ph = self.permission_helper
        pk = getattr(obj, self.opts.pk.attname)

        if ph.user_can_edit_obj(usr, obj):
            btns += self.state_buttons(obj, pk)
        return btns


class ProjectAdmin(ModelAdmin):
    model = Project
    menu_icon = 'fa-product-hunt'
    menu_label = 'Projects'
    list_display = ('company', 'recruiter', 'location', 'daily_rate', 'state')
    list_filter = ('location', 'state')
    search_fields = ('project_page__title',)
    button_helper_class = ProjectButtonHelper
    url_helper_class = ProjectURLHelper

    def get_form_fields_exclude(self, request):
        global_fields = super().get_form_fields_exclude(request)
        state_action = request.resolver_match.kwargs.get('action')
        if state_action:
            transitions = [transition for transition in Project().get_all_state_transitions() if
                           transition.method.__name__ == state_action]
            if not transitions:
                raise Http404
            transition = transitions[0]
            all_fields = [field.name for field in Project._meta.get_fields()]
            focus_fields = transition.custom.get('fields', [])

            fields = list(set(all_fields) - set(focus_fields))
            fields = list(set(fields + global_fields))
        else:
            fields = global_fields
        return fields

    def state_view(self, request, instance_pk, action):
        kwargs = {'model_admin': self, 'instance_pk': instance_pk, 'action': action}
        return StateTransitionView.as_view(**kwargs)(request)

    def get_admin_urls_for_registration(self):
        urls = super().get_admin_urls_for_registration()
        route = url(self.url_helper.get_action_url_pattern('state'),
                    self.state_view,
                    name=self.url_helper.get_action_url_name('state'))
        urls = urls + (route,)
        return urls


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


# Now you just need to register your customised ModelAdmin class with Wagtail
modeladmin_register(CRMGroup)


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


class ProjectSearchArea(SearchArea):
    def __init__(self):
        super().__init__(
            "Projects", reverse('crm_project_modeladmin_index'),
            name='projects',
            classnames='icon icon-fa-product-hunt',
            order=101)


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

from wagtail.contrib.modeladmin.helpers import ButtonHelper
from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register, ModelAdminGroup)
from django.contrib.admin.utils import quote

from crm.models import Recruiter, City, Channel, Project, Employee


class CityAdmin(ModelAdmin):
    model = City
    menu_icon = 'fa-location-arrow'
    menu_label = 'Cities'
    list_display = ('name', 'project_count')


class ChannelAdmin(ModelAdmin):
    model = Channel
    menu_icon = 'fa-arrow-circle-up'
    menu_label = 'Channels'


class ProjectButtonHelper(ButtonHelper):
    def state_buttons(self, obj, pk):
        available_transitions = obj.get_available_state_transitions()
        buttons = []
        for transition in available_transitions:
            buttons.append(
                {
                    'url': self.url_helper.get_action_url('edit', quote(pk)),
                    'label': transition.method.__name__.capitalize(),
                    'classname': self.finalise_classname(['fa-building', 'button-small'] +
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
    list_display = ('recruiter', 'location', 'daily_rate', 'company')
    search_fields = ('project_page__title',)
    button_helper_class = ProjectButtonHelper


class EmployeeAdmin(ModelAdmin):
    model = Employee
    menu_icon = 'fa-users'
    menu_label = 'People'
    search_fields = ('first_name', 'last_name', 'company__name', 'email')
    list_display = ('first_name', 'last_name', 'company', 'project_count')


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


class CRMGroup(ModelAdminGroup):
    menu_label = "CRM"
    menu_icon = "fa-briefcase"
    menu_order = 200
    items = (
        ProjectAdmin, EmployeeAdmin, RecruiterAdmin, CityAdmin, ChannelAdmin
    )


# Now you just need to register your customised ModelAdmin class with Wagtail
modeladmin_register(CRMGroup)

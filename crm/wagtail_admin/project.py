from datetime import timedelta

from django.conf.urls import url
from django.contrib.admin.utils import quote
from django.http import Http404
from django.shortcuts import redirect
from django.template.defaultfilters import pluralize
from django.urls import reverse
from django.utils import timezone
from django_fsm import TransitionNotAllowed
from wagtail.admin import messages
from wagtail.admin.search import SearchArea
from wagtail.contrib.modeladmin.helpers import AdminURLHelper, ButtonHelper
from wagtail.contrib.modeladmin.mixins import ThumbnailMixin
from wagtail.contrib.modeladmin.options import ModelAdmin
from wagtail.contrib.modeladmin.views import EditView, CreateView

from crm.models import Project, ProjectMessage


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


class CreateProjectView(CreateView):
    def form_valid(self, form):
        instance = form.save()
        messages.success(
            self.request, self.get_success_message(instance),
            buttons=self.get_success_message_buttons(instance)
        )

        messages.info(
            self.request,
            "Now you can create CV for this project"
        )

        cv_create_url = f"{reverse('crm_cv_modeladmin_create')}?for_project={instance.pk}"
        return redirect(cv_create_url)

    def get_initial(self):
        next_month_first_day = (timezone.now() + timedelta(days=30)).replace(day=1)

        return {
            'start_date': next_month_first_day,
            'end_date': next_month_first_day.replace(month=next_month_first_day.month + 3)
        }


class ProjectAdmin(ThumbnailMixin, ModelAdmin):
    model = Project
    menu_icon = 'fa-product-hunt'
    menu_label = 'Projects'

    list_display = ('admin_thumb', 'name', 'manager', 'location', 'state', 'last_activity')
    list_filter = ('location', 'state')
    list_per_page = 10
    list_select_related = ['manager', 'location']

    search_fields = ('project_page__title', 'manager__company__name', 'name', 'company__name')
    button_helper_class = ProjectButtonHelper
    url_helper_class = ProjectURLHelper
    ordering = ('-modified',)
    inspect_view_enabled = True
    inspect_view_fields = [
        'state', 'recruiter', 'company', 'location',
        'original_description', 'original_url', 'notes',
        'start_date', 'end_date', 'duration', 'daily_rate', 'working_days',
        'budget', 'vat', 'invoice_amount', 'income_tax', 'nett_income',
        'project_page',
    ]
    thumb_image_field_name = 'logo'
    thumb_default = "/static/img/default_project.png"
    list_display_add_buttons = 'name'
    create_view_class = CreateProjectView

    def last_activity(self, instance):
        days = (timezone.now() - instance.modified).days
        return f"{days} day{pluralize(days)} ago"

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

    def get_extra_attrs_for_field_col(self, obj, field_name):
        if field_name == 'state':
            return {
                "style": f"color: {obj.state_color};text-transform: uppercase;"
            }
        return {}


class ProjectSearchArea(SearchArea):
    def __init__(self):
        super().__init__(
            "Projects", reverse('crm_project_modeladmin_index'),
            name='projects',
            classnames='icon icon-fa-product-hunt',
            order=101)


class MessageAdmin(ModelAdmin):
    model = ProjectMessage
    menu_icon = 'fa-envelope-open'
    menu_label = 'Messages'
    list_display = ['subject', 'author', 'project', 'created']
    list_filter = ['project', 'author']
    ordering = ['-created']
    inspect_view_enabled = True
    inspect_view_fields = ['project', 'subject', 'author', 'text']

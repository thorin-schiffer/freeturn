import logging
from datetime import timedelta

from django.conf.urls import url
from django.contrib.admin.utils import quote
from django.forms import CharField, HiddenInput
from django.shortcuts import redirect, get_object_or_404
from django.template import Template, Context
from django.template.defaultfilters import pluralize
from django.urls import reverse
from django.utils import timezone
from django_filters.fields import ModelChoiceField
from django_fsm import TransitionNotAllowed
from google.api_core.exceptions import GoogleAPIError
from instance_selector.widgets import InstanceSelectorWidget
from wagtail.admin import messages
from wagtail.admin.forms import WagtailAdminModelForm
from wagtail.admin.rich_text import get_rich_text_editor_widget
from wagtail.admin.search import SearchArea
from wagtail.contrib.modeladmin.helpers import AdminURLHelper, ButtonHelper
from wagtail.contrib.modeladmin.mixins import ThumbnailMixin
from wagtail.contrib.modeladmin.options import ModelAdmin
from wagtail.contrib.modeladmin.views import CreateView, InspectView, ModelFormView, \
    InstanceSpecificView
from wagtail.tests.utils.form_data import rich_text

from crm import gmail_utils
from crm.models import City, CV, MessageTemplate
from crm.models.project import Project

logger = logging.getLogger(__file__)


class ProjectURLHelper(AdminURLHelper):
    def get_action_url_pattern(self, action):
        if action == 'state':
            return r'^{}/{}/{}/(?P<instance_pk>[-\w]+)/(?P<action>[-\w]+)/$'.format(
                self.opts.app_label, self.opts.model_name, action
            )
        pattern = super().get_action_url_pattern(action)
        return pattern


class StateTransitionForm(WagtailAdminModelForm):
    template = ModelChoiceField(queryset=MessageTemplate.objects.all(),
                                widget=InstanceSelectorWidget(model=MessageTemplate))

    text = CharField(widget=get_rich_text_editor_widget(),
                     help_text="Change template text in 'Settings' > 'Message templates'",
                     initial='Write your message here...')
    cv = ModelChoiceField(queryset=CV.objects.all(),
                          label='CV',
                          widget=InstanceSelectorWidget(model=CV),
                          required=False)

    def __init__(self, **kwargs):
        # start here
        # add cv attachment checkbox
        project = kwargs['instance']
        data = kwargs.get('data', {})
        action = kwargs.pop('action')
        kwargs['initial']['template'] = project.get_message_template(action)
        template_pk = data.get('template')
        if template_pk:
            self.message_template = get_object_or_404(MessageTemplate, pk=data.get('template'))
            kwargs['data'] = data.copy()
            kwargs['data']['text'] = kwargs['data'].get('text') or rich_text(
                Template(self.message_template.text).render(Context({'project': project}))
            )
            if self.message_template.attach_cv:
                kwargs['data']['cv'] = kwargs['data'].get('cv') or project.cvs.first()
        else:
            self.message_template = None
        super().__init__(**kwargs)

        if template_pk:
            self.fields['template'].widget = HiddenInput()
        else:
            self.fields.pop('text')
            self.fields.pop('cv')
            self.next = True

    class Meta:
        model = Project
        fields = ['template', 'text', 'cv']


class StateTransitionView(ModelFormView, InstanceSpecificView):
    action = None
    form_class = StateTransitionForm
    template_name = 'state.html'

    def __init__(self, **kwargs):
        self.action = kwargs.pop('action')
        self.page_title = f'{self.action.capitalize()} {Project._meta.verbose_name}: write your message'
        super().__init__(**kwargs)

    def get_context_data(self, form=None, **kwargs):
        context = super().get_context_data(form, **kwargs)
        if not self.request.user.social_auth.filter(provider='google-oauth2').exists():
            messages.error(self.request,
                           "Message won't be sent, because no google social auth connection is configured. "
                           "Go to 'AccountSetting'->'More actions' -> 'Google Login'.")
        if self.instance.manager is None:
            messages.error(self.request,
                           "Project doesn't have a manager, messages can't be sent",
                           buttons=[
                               messages.button(text='EDIT', url=reverse('crm_project_modeladmin_edit',
                                                                        kwargs={'instance_pk': self.instance.pk}))
                           ])
        transitions = list(Project._meta.get_field('state').get_all_transitions(Project))
        context['transition'] = next(transition for transition in transitions if transition.name == self.action)
        return context

    def get_form_kwargs(self):
        return {'action': self.action, **super().get_form_kwargs()}

    def get_form_class(self):
        return StateTransitionForm

    def get_success_message(self, instance):
        return "{model_name} '{instance}' now in state {instance.state}".format(
            model_name=self.verbose_name.capitalize(), instance=instance
        )

    def send_mail(self, data):
        from_user = self.request.user
        to_email = self.instance.manager.email
        text = data['text']
        cv = data['cv']
        project_message = self.instance.messages.first()

        try:
            gmail_utils.send_email(
                from_user=from_user,
                to_email=to_email,
                rich_text=text,
                cv=cv,
                project_message=project_message
            )
        except GoogleAPIError as ex:
            logger.error(f"Can't send messages: {ex}")
            messages.error(self.request, f"Can't send messages: {ex}")
            return
        except gmail_utils.NoSocialAuth:
            return
        messages.success(self.request,
                         f'Message sent to {to_email}')

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if self.request.POST.get('next'):
            return self.render_to_response(self.get_context_data(form=form))
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        method = getattr(form.instance, self.action)

        try:
            method()
            if self.request.POST.get('change_state') != 'change_state':
                self.send_mail(data=form.cleaned_data)
        except TransitionNotAllowed:
            return self.form_invalid(form)
        return super().form_valid(form)


class ProjectButtonHelper(ButtonHelper):
    def state_buttons(self, obj, pk):
        available_transitions = obj.get_available_state_transitions()
        buttons = []
        small = not isinstance(self.view, InspectView)
        for transition in available_transitions:
            action = transition.method.__name__
            buttons.append(
                {
                    'url': self.url_helper.get_action_url('state', quote(pk), action),
                    'label': action.capitalize(),
                    'classname': self.finalise_classname(
                        ['button-small' if small else 'button'] +
                        transition.custom.get('classes', [])
                    ),
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
            'Now you can create CV for this project'
        )

        cv_create_url = f"{reverse('crm_cv_modeladmin_create')}?for_project={instance.pk}"
        return redirect(cv_create_url)

    def get_initial(self):
        next_month_first_day = (timezone.now() + timedelta(days=30)).replace(day=1)
        return {
            'start_date': next_month_first_day,
            'end_date': (next_month_first_day + timedelta(days=90)).replace(day=1),
            'location': City.most_popular()
        }


class ProjectAdmin(ThumbnailMixin, ModelAdmin):
    model = Project
    menu_icon = 'fa-product-hunt'
    menu_label = 'Projects'

    list_display = ('admin_thumb', 'name', 'manager', 'location', 'state', 'last_activity')
    list_per_page = 5
    list_select_related = ['manager', 'location']

    search_fields = ('project_page__title', 'manager__company__name', 'name', 'company__name',
                     'manager__first_name', 'manager__last_name')
    button_helper_class = ProjectButtonHelper
    url_helper_class = ProjectURLHelper
    ordering = ('-modified',)
    inspect_view_enabled = True
    inspect_view_fields = [
        'state', 'company', 'location',
        'original_description', 'original_url', 'notes',
        'start_date', 'end_date', 'duration', 'daily_rate', 'working_days',
        'budget', 'vat', 'invoice_amount', 'income_tax', 'nett_income',
        'project_page', 'logo'
    ]
    inspect_template_name = 'project_inspect.html'
    thumb_image_field_name = 'logo'
    thumb_default = '/static/img/default_project.png'
    list_display_add_buttons = 'name'
    create_view_class = CreateProjectView

    def last_activity(self, instance):
        days = (timezone.now() - instance.modified).days
        return f'{days} day{pluralize(days)} ago'

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
                'style': f'color: {obj.state_color};text-transform: uppercase;'
            }
        return {}


class ProjectSearchArea(SearchArea):
    def __init__(self):
        super().__init__(
            'Projects', reverse('crm_project_modeladmin_index'),
            name='projects',
            classnames='icon icon-fa-product-hunt',
            order=101)

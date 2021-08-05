from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from wagtail.admin.edit_handlers import ObjectList
from wagtail.contrib.modeladmin.mixins import ThumbnailMixin
from wagtail.contrib.modeladmin.options import ModelAdmin
from wagtail.contrib.modeladmin.views import CreateView, InspectView, EditView
from wagtail.core.models import Site

from crm.models.cv import CV
from crm.models.project import Project
from crm.models.settings import CVGenerationSettings
from crm.utils import BasePDFView


class CreateCVView(CreateView):
    def get_edit_handler(self):
        if hasattr(self.model, 'edit_handler'):
            edit_handler = self.model.edit_handler
        else:
            edit_handler = ObjectList(CV.create_panels)
        return edit_handler.bind_to(self.model)

    def get_initial(self):
        site = Site.find_for_request(self.request)
        user = self.request.user
        settings = CVGenerationSettings.for_site(site)
        try:
            for_project = Project.objects.filter(pk=self.request.GET.get('for_project')).first()
        except ValueError:
            for_project = None
        return {
            'title': settings.default_title,
            'experience_overview': settings.default_experience_overview,
            'education_overview': settings.default_education_overview,
            'contact_details': settings.default_contact_details,
            'languages_overview': settings.default_languages_overview,
            'rate_overview': settings.default_rate_overview,
            'working_permit': settings.default_working_permit,
            'full_name': f'{user.first_name} {user.last_name}',
            'picture': settings.default_picture,
            'project': for_project
        }


class CVInspectView(BasePDFView,
                    InspectView):
    template_name = 'cv/body.html'

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **self.instance.get_default_file_render_context()
        }

    def get_filename(self):
        return self.instance.get_filename()


class CVEditView(EditView):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if request.method == 'POST':
            return redirect(
                self.url_helper.get_action_url('edit', self.pk_quoted)
            )
        else:
            return response


class CVAdmin(ThumbnailMixin, ModelAdmin):
    model = CV
    menu_icon = 'fa-id-card'
    menu_label = 'CVs'
    create_view_class = CreateCVView
    list_display = ['admin_thumb', 'project', 'created']
    search_fields = ['project__manager__first_name', 'project__manager__last_name',
                     'project__name', 'project__company__name']
    list_per_page = 10
    list_select_related = ['project']
    ordering = ['-created']
    inspect_view_enabled = True
    inspect_view_class = CVInspectView
    inspect_template_name = CVInspectView.template_name
    thumb_image_field_name = 'logo'
    thumb_default = '/static/img/default_project.png'
    list_display_add_buttons = 'project'
    edit_view_class = CVEditView

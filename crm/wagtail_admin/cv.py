from django.db.models import Count
from wagtail.admin.edit_handlers import ObjectList
from wagtail.contrib.modeladmin.mixins import ThumbnailMixin
from wagtail.contrib.modeladmin.options import ModelAdmin
from wagtail.contrib.modeladmin.views import CreateView, InspectView
from wkhtmltopdf.views import PDFTemplateView

from crm.models import CV, CVGenerationSettings, Project
from home.models import Technology, ProjectPage


class CreateCVView(CreateView):
    def get_edit_handler(self):
        if hasattr(self.model, 'edit_handler'):
            edit_handler = self.model.edit_handler
        else:
            edit_handler = ObjectList(CV.create_panels)
        return edit_handler.bind_to_model(self.model)

    def get_initial(self):
        site = self.request.site
        user = self.request.user
        settings = CVGenerationSettings.for_site(site)
        try:
            for_project = Project.objects.filter(pk=self.request.GET.get('for_project')).first()
        except ValueError:
            for_project = None
        return {
            "title": settings.default_title,
            "experience_overview": settings.default_experience_overview,
            "education_overview": settings.default_education_overview,
            "contact_details": settings.default_contact_details,
            "languages_overview": settings.default_languages_overview,
            "rate_overview": settings.default_rate_overview,
            "working_permit": settings.default_working_permit,
            "full_name": f"{user.first_name} {user.last_name}",
            "picture": settings.default_picture,
            "project": for_project
        }


class CVInspectView(PDFTemplateView,
                    InspectView):
    show_content_in_browser = True
    template_name = "cv/body.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['skills'] = Technology.objects.annotate(
            projects_count=Count('projects')
        ).filter(projects_count__gt=0).order_by('-projects_count')
        context['project_pages'] = ProjectPage.objects.live().order_by('-start_date')
        context['relevant_project_pages'] = self.instance.relevant_project_pages.order_by('-start_date')
        return context

    def get_filename(self):
        return f"{self.instance.full_name} CV and project portfolio for {self.instance.project}.pdf"


class CVAdmin(ThumbnailMixin, ModelAdmin):
    model = CV
    menu_icon = 'fa-id-card'
    menu_label = 'CVs'
    create_view_class = CreateCVView
    list_display = ['admin_thumb', 'project', 'created']
    list_filter = ['project__manager']
    list_per_page = 10
    list_select_related = ['project']
    ordering = ['-created']
    inspect_view_enabled = True
    inspect_view_class = CVInspectView
    inspect_template_name = CVInspectView.template_name
    thumb_image_field_name = 'logo'
    thumb_default = "/static/img/default_project.png"
    list_display_add_buttons = 'project'

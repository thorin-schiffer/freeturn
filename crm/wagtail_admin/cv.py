from wagtail.contrib.modeladmin.options import ModelAdmin
from wagtail.contrib.modeladmin.views import CreateView

from crm.models import CV, CVGenerationSettings


class CreateCVView(CreateView):
    def get_initial(self):
        site = self.request.site
        settings = CVGenerationSettings.for_site(site)
        return {
            "title": settings.default_title,
            "experience_overview": settings.default_experience_overview,
            "education_overview": settings.default_education_overview,
            "contact_details": settings.default_contact_details,
            "languages_overview": settings.default_languages_overview,
            "rate_overview": settings.default_rate_overview
        }


class CVAdmin(ModelAdmin):
    model = CV
    menu_icon = 'fa-id-card'
    menu_label = 'CVs'
    create_view_class = CreateCVView

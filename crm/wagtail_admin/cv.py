from wagtail.contrib.modeladmin.options import ModelAdmin
from wagtail.contrib.modeladmin.views import CreateView

from crm.models import CV, CVGenerationSettings
from home.models import HomePage


class CreateCVView(CreateView):
    def get_initial(self):
        site = self.request.site
        user = self.request.user
        settings = CVGenerationSettings.for_site(site)
        home = HomePage.objects.live().first()
        return {
            "title": settings.default_title,
            "experience_overview": settings.default_experience_overview,
            "education_overview": settings.default_education_overview,
            "contact_details": settings.default_contact_details,
            "languages_overview": settings.default_languages_overview,
            "rate_overview": settings.default_rate_overview,
            "working_permit": settings.default_working_permit,
            "full_name": f"{user.first_name} {user.last_name}",
            "earliest_available": home.earliest_available,
            "picture": home.picture
        }


class CVAdmin(ModelAdmin):
    model = CV
    menu_icon = 'fa-id-card'
    menu_label = 'CVs'
    create_view_class = CreateCVView

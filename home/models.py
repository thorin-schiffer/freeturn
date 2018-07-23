from django.db import models
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.fields import RichTextField
from wagtail.core.models import Page
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index


class HomePage(Page):
    pass


class PortfolioPage(Page):
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['projects'] = ProjectPage.objects.all()
        return context


class ProjectPage(Page):
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    name = models.CharField(max_length=255)

    summary = RichTextField(help_text="Short description to show on tiles and lists")
    description = RichTextField(help_text="Long description to show on the detail page")

    start_date = models.DateField(null=True, blank=True)
    duration = models.IntegerField(help_text="Duration in months, null=till now",
                                   null=True, blank=True)

    search_fields = Page.search_fields + [
        index.SearchField('name'),
        index.SearchField('summary'),
        index.FilterField('start_date'),
    ]

    content_panels = Page.content_panels + [
        ImageChooserPanel('logo'),
        FieldPanel('name'),
        FieldPanel('summary'),
        FieldPanel('description'),

        FieldPanel('start_date'),
        FieldPanel('duration'),

    ]

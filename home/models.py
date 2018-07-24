from django.db import models
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase
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
        technology = request.GET.get('technology')
        context['projects'] = ProjectPage.objects.child_of(self).live()
        if technology:
            context['projects'] = context['projects'].filter(technologies__name=technology)
        return context


class ProjectTechnology(TaggedItemBase):
    content_object = ParentalKey('ProjectPage', on_delete=models.CASCADE,
                                 related_name='technologies_items')


class ProjectPage(Page):
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    name = models.CharField(max_length=255)

    summary = models.CharField(max_length=511,
                               help_text="Short description to show on tiles and lists")
    description = RichTextField(help_text="Long description to show on the detail page")

    start_date = models.DateField(null=True, blank=True)
    duration = models.IntegerField(help_text="Duration in months, null=till now",
                                   null=True, blank=True)

    responsibility = RichTextField()

    search_fields = Page.search_fields + [
        index.SearchField('name'),
        index.SearchField('summary'),
        index.RelatedFields('technologies', [
            index.SearchField('name', partial_match=True, boost=10),
        ]),
        index.FilterField('start_date'),
    ]

    technologies = ClusterTaggableManager(through=ProjectTechnology,
                                          blank=True)

    content_panels = Page.content_panels + [
        ImageChooserPanel('logo'),
        FieldPanel('name'),
        FieldPanel('summary'),
        FieldPanel('description'),

        FieldPanel('start_date'),
        FieldPanel('duration'),
        FieldPanel('responsibility'),
        FieldPanel('technologies'),
    ]

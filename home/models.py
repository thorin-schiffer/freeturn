from datetime import timedelta

from ajax_select.fields import AutoCompleteSelectMultipleWidget
from colorful.fields import RGBColorField
from django.db import models
from django.db.models import Count
from django.utils import timezone
from fuzzywuzzy import process
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, FieldRowPanel
from wagtail.contrib.forms.edit_handlers import FormSubmissionsPanel
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.core.fields import RichTextField
from wagtail.core.models import Page
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.documents.models import get_document_model
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from home.forms import RecaptchaForm


class HomePage(Page):
    background = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    claim = models.CharField(max_length=300,
                             help_text="Claim text placed under the name",
                             default="Freelance python developer")
    title_color = RGBColorField(default="#FFFFFF")

    picture = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="My picture"
    )
    max_count = 1
    subpage_types = [
        'home.PortfolioPage',
        'home.TechnologiesPage',
        'home.ContactPage'
    ]

    earliest_available = models.DateField(null=True, blank=True, default=timezone.now)

    content_panels = Page.content_panels + [
        FieldPanel('title_color'),
        FieldPanel('claim'),
        FieldPanel('earliest_available'),
        ImageChooserPanel('picture'),
        ImageChooserPanel('background'),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['forms'] = ContactPage.objects.live()
        current_project = ProjectPage.objects.live().filter(
            start_date__lt=timezone.now()
        ).order_by('-start_date').first()
        context['current_project'] = current_project

        last_project = ProjectPage.objects.live().order_by('-start_date').first()
        context['earliest_available'] = self.earliest_available or last_project.start_date + timedelta(
            days=31 * (last_project.duration or 1)
        )
        return context


class PortfolioPage(Page):
    background = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    max_count = 1
    subpage_types = [
        'home.ProjectPage',
    ]

    content_panels = Page.content_panels + [
        ImageChooserPanel('background'),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        technology = request.GET.get('technology')
        context['projects'] = ProjectPage.objects.child_of(self).live()
        if technology:
            context['projects'] = context['projects'].filter(technologies__name__in=[technology.lower()])
            context['technology'] = Technology.objects.filter(name=technology).first()
        context['projects'] = context['projects'].order_by('-start_date')
        return context


class ProjectPage(Page):
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    card_background = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Card background on the portfolio view"
    )

    summary = models.CharField(max_length=511,
                               help_text="Short description to show on tiles and lists")
    description = RichTextField(help_text="Long description to show on the detail page")

    start_date = models.DateField(null=True, blank=True, db_index=True)
    duration = models.IntegerField(help_text="Duration in months, null=till now",
                                   null=True, blank=True)

    position = models.CharField(max_length=100,
                                default="Backend developer")

    search_fields = Page.search_fields + [
        index.SearchField('summary'),
        index.RelatedFields('technologies', [
            index.SearchField('name', partial_match=True, boost=10),
        ]),
        index.FilterField('start_date'),
    ]

    technologies = ParentalManyToManyField(
        'Technology',
        related_name="projects",
        blank=True
    )
    project_url = models.URLField(null=True, blank=True)  # url is a part of the parent model

    reference_letter = models.ForeignKey(
        get_document_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Reference letter for this project"
    )
    responsibilities = ParentalManyToManyField(
        'Responsibility',
        related_name="projects",
        blank=True
    )
    content_panels = Page.content_panels + [
        ImageChooserPanel('logo'),
        ImageChooserPanel('card_background'),
        FieldPanel('summary'),
        FieldPanel('description'),
        FieldPanel('project_url'),
        FieldPanel('start_date'),
        FieldPanel('duration'),
        FieldPanel('position'),
        FieldPanel('technologies', widget=AutoCompleteSelectMultipleWidget('technologies')),
        FieldPanel('responsibilities'),
        DocumentChooserPanel('reference_letter'),
    ]
    subpage_types = []

    @property
    def end_date(self):
        return self.start_date + timedelta(days=30 * self.duration)

    class Meta:
        ordering = ('-start_date',)


class TechnologiesPage(Page):
    background = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    title_color = RGBColorField(default="#FFFFFF")

    content_panels = Page.content_panels + [
        FieldPanel('title_color'),
        ImageChooserPanel('background'),
    ]
    subpage_types = []
    max_count = 1

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['technologies'] = Technology.objects.annotate(
            projects_count=Count('projects')
        ).filter(projects_count__gt=0).order_by('-projects_count')
        context['portfolio'] = PortfolioPage.objects.last()
        return context


@register_snippet
class Technology(index.Indexed, models.Model):
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    summary = RichTextField(blank=True)
    name = models.CharField(max_length=100, unique=True)
    match_in_cv = models.BooleanField(default=True,
                                      help_text="Match for technology in CV relevant projects?")
    panels = [
        FieldPanel('name'),
        ImageChooserPanel('logo'),
        FieldPanel('summary'),
    ]
    search_fields = [
        index.SearchField('name', partial_match=True),
    ]

    @staticmethod
    def match_text(text, limit=5, cutoff=40):
        choices = Technology.objects.filter(match_in_cv=True).values_list(
            'name', flat=True
        )
        if not choices.exists():
            return Technology.objects.none()
        results = process.extract(text, choices, limit=limit)
        return Technology.objects.filter(
            name__in=[r[0] for r in results if r[1] > cutoff]
        )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'technology'
        verbose_name_plural = 'technologies'


class FormField(AbstractFormField):
    page = ParentalKey('ContactPage', on_delete=models.CASCADE, related_name='form_fields')


class ContactPage(RecaptchaForm):
    background = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)

    content_panels = AbstractEmailForm.content_panels + [
        FormSubmissionsPanel(),
        FieldPanel('intro', classname="full"),
        InlinePanel('form_fields', label="Form fields"),
        FieldPanel('thank_you_text', classname="full"),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('from_address', classname="col6"),
                FieldPanel('to_address', classname="col6"),
            ]),
            FieldPanel('subject'),
        ], "Email"),
    ]


@register_snippet
class Responsibility(models.Model):
    text = models.CharField(max_length=200)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name_plural = "responsibilities"

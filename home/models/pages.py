from datetime import timedelta

from django.db import models
from django.db.models import Count
from django.utils import timezone
from modelcluster.fields import ParentalManyToManyField, ParentalKey
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, FieldRowPanel
from wagtail.contrib.forms.edit_handlers import FormSubmissionsPanel
from wagtail.contrib.forms.models import AbstractFormField, AbstractEmailForm
from wagtail.core.fields import RichTextField
from wagtail.core.models import Page
from wagtail.documents import get_document_model_string
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtailautocomplete.edit_handlers import AutocompletePanel

from home.forms import RecaptchaForm
from home.models.snippets import Technology


class HomePage(Page):
    background = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    claim = models.CharField(max_length=300,
                             help_text='Claim text placed under the name',
                             default='Freelance python developer')
    services = models.CharField(max_length=500,
                                help_text='Services you want to highlight',
                                default='Python, Django, Wagtail')
    picture = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='My picture'
    )
    max_count = 1
    subpage_types = [
        'home.PortfolioPage',
        'home.TechnologiesPage',
        'home.ContactPage'
    ]

    earliest_available = models.DateField(null=True, blank=True, default=timezone.now)

    stackoverflow_profile = models.URLField(null=True, blank=True)
    github_profile = models.URLField(null=True, blank=True)
    linkedin_profile = models.URLField(null=True, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('claim'),
        FieldPanel('earliest_available'),
        ImageChooserPanel('picture'),
        ImageChooserPanel('background'),
        FieldPanel('stackoverflow_profile'),
        FieldPanel('github_profile'),
        FieldPanel('linkedin_profile'),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['forms'] = ContactPage.objects.filter(show_on_home=True).live()
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
    summary = models.CharField(max_length=511,
                               help_text='Short description to show on tiles and lists')
    description = RichTextField(help_text='Long description to show on the detail page')

    start_date = models.DateField(null=True, blank=True, db_index=True)
    duration = models.IntegerField(help_text='Duration in months, null=till now',
                                   null=True, blank=True)

    position = models.CharField(max_length=100,
                                default='Backend developer')

    search_fields = Page.search_fields + [
        index.SearchField('summary'),
        index.RelatedFields('technologies', [
            index.SearchField('name', partial_match=True, boost=10),
        ]),
        index.FilterField('start_date'),
    ]

    technologies = ParentalManyToManyField(
        'Technology',
        related_name='projects',
        blank=True
    )
    project_url = models.URLField(null=True, blank=True)  # url is a part of the parent model

    reference_letter = models.ForeignKey(
        get_document_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Reference letter for this project'
    )
    responsibilities = ParentalManyToManyField(
        'Responsibility',
        related_name='projects',
        blank=True
    )
    content_panels = Page.content_panels + [
        ImageChooserPanel('logo'),
        FieldPanel('summary'),
        FieldPanel('description'),
        FieldPanel('project_url'),
        FieldPanel('start_date'),
        FieldPanel('duration'),
        FieldPanel('position'),
        AutocompletePanel('technologies', target_model=Technology),
        FieldPanel('responsibilities'),
        DocumentChooserPanel('reference_letter'),
    ]
    subpage_types = []

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

    content_panels = Page.content_panels + [
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
    show_on_home = models.BooleanField(default=False,
                                       help_text='Show link to this form on home page?')
    content_panels = AbstractEmailForm.content_panels + [
        FormSubmissionsPanel(),
        FieldPanel('intro', classname='full'),
        InlinePanel('form_fields', label='Form fields'),
        FieldPanel('thank_you_text', classname='full'),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('from_address', classname='col6'),
                FieldPanel('to_address', classname='col6'),
            ]),
            FieldPanel('subject'),
        ], 'Email'),
    ]
    settings_panels = AbstractEmailForm.settings_panels + [
        FieldPanel('show_on_home')
    ]

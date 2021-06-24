import logging

from django.db import models
from django.db.models import CASCADE
from django.utils import timezone
from django_extensions.db.models import TimeStampedModel
from instance_selector.edit_handlers import InstanceSelectorPanel
from wagtail.admin.edit_handlers import FieldPanel, FieldRowPanel, MultiFieldPanel
from wagtail.core.fields import RichTextField
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtailautocomplete.edit_handlers import AutocompletePanel

from home.models import ProjectPage
from home.models.snippets import Technology

logger = logging.getLogger(__file__)


class CV(TimeStampedModel):
    project = models.ForeignKey('Project',
                                blank=True,
                                null=True,
                                on_delete=CASCADE,
                                related_name='cvs')
    earliest_available = models.DateField(null=True, blank=True, default=timezone.now)
    picture = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Picture to use'
    )

    full_name = models.CharField(max_length=200,
                                 help_text='Name to use in the title of the file, default is current user')
    title = models.CharField(max_length=200, help_text='Title to be placed under the name')
    experience_overview = RichTextField(
        help_text='Notice on your experience',
    )
    project_listing_title = models.CharField(
        max_length=200,
        help_text="The title of your project listing, something like 'my projects' or 'recent projects'",
        default='Recent projects'
    )
    relevant_project_pages = models.ManyToManyField(
        'home.ProjectPage',
        help_text='Project pages to be placed on the first page, eye catcher for this project',
        related_name='applications_highlighted',
        blank=True
    )
    include_portfolio = models.BooleanField(
        default=True,
        help_text="Include portfolio projects' description"
    )
    relevant_skills = models.ManyToManyField(
        'home.Technology',
        help_text='Technologies to be included, '
                  'will be automatically formed to look relevant',
        blank=True
    )

    education_overview = RichTextField(
        help_text='Notice on your education',
    )
    contact_details = RichTextField()
    languages_overview = RichTextField()
    rate_overview = RichTextField(blank=True, null=True)
    working_permit = RichTextField()
    common_panels = [
        ImageChooserPanel('picture'),
        FieldRowPanel(
            [
                MultiFieldPanel(
                    [
                        FieldPanel('full_name'),
                        FieldPanel('title'),
                        FieldPanel('earliest_available'),
                        FieldPanel('experience_overview'),
                        FieldPanel('education_overview'),
                    ],
                    heading='Header data'
                ),
                MultiFieldPanel(
                    [
                        FieldPanel('contact_details'),
                        FieldPanel('languages_overview'),
                        FieldPanel('rate_overview'),
                        FieldPanel('working_permit'),
                    ]
                )

            ]
        ),
    ]
    create_panels = [
        InstanceSelectorPanel('project'),
        *common_panels
    ]
    panels = [
        MultiFieldPanel([
            InstanceSelectorPanel('project'),
            FieldPanel('project_listing_title'),
            AutocompletePanel('relevant_project_pages', is_single=False,
                              page_type='home.ProjectPage'),
            FieldPanel('include_portfolio'),

        ]),
        AutocompletePanel('relevant_skills', target_model=Technology),
        *common_panels
    ]

    @property
    def logo(self):
        return self.project.logo if self.project else None

    def set_relevant_skills_and_projects(self, limit=5):
        technologies = Technology.match_text(self.project.original_description)
        if self.relevant_project_pages.count():
            logger.error(f"Won't set relevant project pages for {self}, it's not empty")
            return
        self.relevant_project_pages.set(ProjectPage.objects.live().filter(
            technologies__in=technologies
        ).order_by('-start_date')[:limit])
        self.relevant_skills.set(technologies)

    def save(self, **kwargs):
        creating = self.pk is None
        super().save(**kwargs)
        if creating and self.project:
            self.set_relevant_skills_and_projects()

    def __str__(self):
        return str(self.project)

    class Meta:
        verbose_name = 'CV'

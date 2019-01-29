import logging
import math

from ajax_select.fields import AutoCompleteSelectMultipleWidget, AutoCompleteSelectWidget
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import CASCADE
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import SafeText
from django_extensions.db.models import TimeStampedModel
from phonenumber_field.modelfields import PhoneNumberField
from tld import get_fld
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, FieldRowPanel, PageChooserPanel
from wagtail.contrib.settings.models import BaseSetting
from wagtail.contrib.settings.registry import register_setting
from wagtail.core.fields import RichTextField
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtailautocomplete.edit_handlers import AutocompletePanel
from wagtailmarkdown.fields import MarkdownField
from wagtailmarkdown.utils import render_markdown

from crm.project_states import ProjectStateMixin
from crm.utils import get_working_days
from home.models import Technology, ProjectPage

logger = logging.getLogger("crm.models")


class City(models.Model):
    name = models.CharField(max_length=200,
                            unique=True)

    @property
    def project_count(self):
        return self.projects.count()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "city"
        ordering = ['name']


class Employee(TimeStampedModel):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    telephone = PhoneNumberField(null=True,
                                 blank=True)
    mobile = PhoneNumberField(null=True,
                              blank=True)

    email = models.EmailField()

    company = models.ForeignKey('Recruiter',
                                on_delete=models.CASCADE)

    picture = models.ForeignKey('wagtailimages.Image', on_delete=models.SET_NULL,
                                null=True, blank=True)

    panels = [
        FieldRowPanel(
            [
                MultiFieldPanel([
                    FieldPanel('first_name'),
                    FieldPanel('last_name'),
                    FieldPanel('telephone'),
                    FieldPanel('mobile'),
                    FieldPanel('email'),
                ]),
                MultiFieldPanel([
                    FieldPanel('company', widget=AutoCompleteSelectWidget('companies')),
                    ImageChooserPanel('picture'),
                ]),
            ]
        ),
    ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} [{self.company}]"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def project_count(self):
        return self.projects.count()

    class Meta:
        verbose_name_plural = 'people'
        ordering = ['-created']


class Channel(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField(blank=True,
                          null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'channels'


class Project(ProjectStateMixin, TimeStampedModel):
    name = models.CharField(max_length=120,
                            blank=True, null=True)
    company = models.ForeignKey('ClientCompany',
                                on_delete=models.SET_NULL,
                                null=True,
                                blank=True,
                                related_name='projects')

    manager = models.ForeignKey('Employee',
                                on_delete=models.SET_NULL,
                                null=True,
                                blank=True,
                                related_name='projects')
    location = models.ForeignKey('crm.City',
                                 related_name='projects',
                                 null=True, blank=True,
                                 on_delete=models.CASCADE)

    original_description = RichTextField()
    original_url = models.URLField(null=True, blank=True)

    notes = MarkdownField(null=True, blank=True)
    daily_rate = models.DecimalField(
        decimal_places=2,
        max_digits=6,
        null=True,
        blank=True
    )

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    project_page = models.ForeignKey('home.ProjectPage',
                                     on_delete=models.SET_NULL,
                                     null=True,
                                     blank=True)

    panels = [
        MultiFieldPanel([
            FieldPanel('name'),
            FieldPanel('original_url'),
            FieldPanel('original_description'),

        ]),
        FieldRowPanel([
            MultiFieldPanel([
                FieldPanel('company', widget=AutoCompleteSelectWidget('companies')),
                FieldPanel('manager'),
                FieldPanel('location')
            ]),
            MultiFieldPanel([
                FieldPanel('daily_rate'),
                FieldPanel('start_date'),
                FieldPanel('end_date')
            ])
        ]),
        FieldPanel('notes'),
        PageChooserPanel('project_page')
    ]

    @property
    def recruiter(self):
        return self.manager.company if self.manager else None

    @property
    def duration(self):
        try:
            return math.ceil((self.end_date - self.start_date).days / 30)
        except TypeError:
            pass

    def get_duration_display(self):
        return f"{self.duration} months"

    def get_original_description_display(self):
        return SafeText(self.original_description)

    def get_notes_display(self):
        return SafeText(render_markdown(self.notes))

    def get_project_page_display(self):
        if not self.project_page:
            return
        url = reverse("wagtailadmin_pages:edit", args=(self.project_page.pk,))
        return SafeText(
            f"<a href='{url}'>{self.project_page}</a>"
        )

    @property
    def budget(self):
        if not self.start_date or not self.end_date:
            return
        working_days = len(get_working_days(self.start_date, self.end_date))
        if not self.daily_rate:
            return
        return self.daily_rate * working_days

    @property
    def vat(self):
        if not self.budget:
            return
        return self.budget * settings.VAT_RATE

    @property
    def invoice_amount(self):
        if not self.vat:
            return
        return self.budget + self.vat

    @property
    def income_tax(self):
        if not self.budget:
            return
        return self.budget * settings.INCOME_TAX_RATE

    @property
    def nett_income(self):
        if not self.budget or not self.income_tax:
            return
        return self.budget - self.income_tax

    @property
    def working_days(self):
        if not self.start_date or not self.end_date:
            return
        return len(get_working_days(self.start_date, self.end_date))

    def get_budget_display(self):
        return f"{self.budget} €" if self.budget else None

    def get_vat_display(self):
        return f"{self.vat:.2f} €" if self.vat else None

    def get_invoice_amount_display(self):
        return f"{self.invoice_amount:.2f} €" if self.invoice_amount else None

    def get_income_tax_display(self):
        return f"{self.income_tax:.2f} €" if self.income_tax else None

    def get_nett_income_display(self):
        return f"{self.nett_income:.2f} €" if self.nett_income else None

    @property
    def logo(self):
        company_logo = self.company.logo if self.company else None
        recruiter_logo = self.recruiter.logo if self.recruiter else None
        return company_logo or recruiter_logo

    def clean(self):
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError(
                {
                    "start_date": "End date can't be earlier than start date",
                    "end_date": "End date can't be earlier than start date",
                }
            )

    def save(self, *args, **kwargs):
        if not self.daily_rate and self.recruiter:
            self.daily_rate = self.recruiter.default_daily_rate
        if not self.name:
            self.name = str(self.company or self.recruiter)
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.company or self.recruiter)

    class Meta:
        verbose_name_plural = "projects"


class ProjectMessage(TimeStampedModel):
    project = models.ForeignKey('Project',
                                null=True,
                                blank=True,
                                on_delete=models.SET_NULL,
                                related_name='messages')
    author = models.ForeignKey('Employee',
                               on_delete=models.CASCADE,
                               related_name='messages')
    sent_at = models.DateTimeField(default=timezone.now,
                                   help_text="Sending time")
    subject = models.CharField(max_length=200,
                               blank=True,
                               null=True)
    text = models.TextField()

    gmail_message_id = models.CharField(max_length=50)
    gmail_thread_id = models.CharField(max_length=50)

    def __str__(self):
        return self.subject


class BaseCompany(TimeStampedModel):
    name = models.CharField(max_length=200,
                            unique=True)
    location = models.ForeignKey('crm.City',
                                 on_delete=models.CASCADE,
                                 blank=True,
                                 null=True)
    channel = models.ForeignKey('Channel',
                                on_delete=models.SET_NULL,
                                help_text="Lead channel this company came from",
                                null=True,
                                blank=True)
    url = models.URLField(blank=True,
                          null=True)
    notes = MarkdownField(default="", blank=True)
    logo = models.ForeignKey('wagtailimages.Image', on_delete=models.SET_NULL,
                             null=True, blank=True)

    panels = [
        FieldRowPanel([
            MultiFieldPanel([
                FieldPanel('name'),
                FieldPanel('location'),
                FieldPanel('url'),
            ]),
            MultiFieldPanel(
                [
                    ImageChooserPanel('logo'),
                    FieldPanel('channel'),
                ]
            )
        ]),
        FieldRowPanel([FieldPanel('notes')])
    ]

    def __str__(self):
        return self.name

    @property
    def domain(self):
        return get_fld(self.url, fail_silently=True)

    class Meta:
        abstract = True
        verbose_name_plural = 'clients'
        verbose_name = 'client'


class Recruiter(BaseCompany):
    default_daily_rate = models.DecimalField(
        decimal_places=2,
        max_digits=6,
        null=True,
        blank=True,
        default=settings.DEFAULT_DAILY_RATE
    )
    panels = BaseCompany.panels + [
        FieldPanel('default_daily_rate')
    ]

    class Meta:
        verbose_name_plural = 'recruiters'


class ClientCompany(BaseCompany):
    pass


class CV(TimeStampedModel):
    project = models.ForeignKey("Project",
                                on_delete=CASCADE,
                                related_name="cvs")
    earliest_available = models.DateField(null=True, blank=True, default=timezone.now)
    picture = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Picture to use, default is the one used on home page"
    )

    full_name = models.CharField(max_length=200,
                                 help_text="Name to use in the title of the file, default is current user")
    title = models.CharField(max_length=200, help_text="Title to be placed under the name")
    experience_overview = MarkdownField(
        help_text="Notice on your experience",
    )

    relevant_project_pages = models.ManyToManyField(
        "home.ProjectPage",
        help_text="Project pages to be placed on the first page, eye catcher for this project",
        related_name="applications_highlighted",
        blank=True
    )
    relevant_skills = models.ManyToManyField(
        'home.Technology',
        help_text="Technologies to be included, "
                  "will be automatically formed to look relevant",
        blank=True
    )

    education_overview = MarkdownField(
        help_text="Notice on your education",
    )
    contact_details = MarkdownField()
    languages_overview = MarkdownField()
    rate_overview = MarkdownField()
    working_permit = MarkdownField()

    create_panels = [
        FieldPanel('project'),
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
                    heading="Header data"
                ),
                MultiFieldPanel(
                    [
                        ImageChooserPanel('picture'),
                        FieldPanel('contact_details'),
                        FieldPanel('languages_overview'),
                        FieldPanel('rate_overview'),
                        FieldPanel('working_permit'),
                    ]
                )

            ]
        ),
    ]
    panels = [
                 AutocompletePanel('relevant_project_pages', is_single=False, page_type='home.ProjectPage'),
                 FieldPanel('relevant_skills', widget=AutoCompleteSelectMultipleWidget('technologies')),
             ] + create_panels

    def set_relevant_skills_and_projects(self, limit=5):
        technologies = Technology.match_text(self.project.original_description)
        if self.relevant_project_pages.count():
            logger.error(f"Won't set relevant project pages for {self}, it's not empty")
            return
        self.relevant_project_pages.set(ProjectPage.objects.live().filter(
            technologies__in=technologies
        ).order_by('-start_date')[:limit])
        self.relevant_skills.set(technologies)

    @property
    def logo(self):
        return self.project.logo if self.project else None

    def save(self, **kwargs):
        creating = self.pk is None
        super().save(**kwargs)
        if creating:
            self.set_relevant_skills_and_projects()

    def __str__(self):
        return str(self.project)

    class Meta:
        verbose_name = "CV"


@register_setting(icon='icon icon-fa-id-card')
class CVGenerationSettings(BaseSetting):
    default_title = models.CharField(
        max_length=255, help_text='Default title to use', default="Freelance python developer")
    default_experience_overview = MarkdownField(
        help_text="Notice on your experience",
        default="Python developer experience: 7 years"
    )

    default_education_overview = MarkdownField(
        help_text="Notice on your education",
        default="Novosibirsk State Technical University"
    )
    default_contact_details = MarkdownField(default="sergey@cheparev.com")
    default_languages_overview = MarkdownField(default="English: fluent")
    default_rate_overview = MarkdownField(default="<<change default in settings>>")
    default_working_permit = MarkdownField(default="PERMANENT RESIDENCE")
    default_picture = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    panels = [
        FieldPanel('default_title'),
        FieldPanel('default_experience_overview'),
        FieldPanel('default_education_overview'),
        FieldPanel('default_contact_details'),
        FieldPanel('default_languages_overview'),
        FieldPanel('default_rate_overview'),
        FieldPanel('default_working_permit'),
        FieldPanel('default_rate_overview'),
        ImageChooserPanel('default_picture')
    ]

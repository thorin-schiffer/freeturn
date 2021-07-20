import math

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import CharField
from django.urls import reverse
from django.utils.safestring import SafeText
from django_extensions.db.models import TimeStampedModel
from django_fsm import FSMField, transition
from instance_selector.edit_handlers import InstanceSelectorPanel
from wagtail.admin.edit_handlers import MultiFieldPanel, FieldPanel, FieldRowPanel, PageChooserPanel
from wagtail.core.fields import RichTextField
from wagtail.core.models import Site

from crm.models import CV
from crm.models.settings import CVGenerationSettings
from crm.utils import get_working_days


class ProjectDisplayMixin:
    def get_project_page_display(self):
        if not self.project_page:
            return
        url = reverse('wagtailadmin_pages:edit', args=(self.project_page.pk,))
        return SafeText(
            f"<a href='{url}'>{self.project_page}</a>"
        )

    def get_budget_display(self):
        return f'{self.budget} €' if self.budget else None

    def get_vat_display(self):
        return f'{self.vat:.2f} €' if self.vat else None

    def get_invoice_amount_display(self):
        return f'{self.invoice_amount:.2f} €' if self.invoice_amount else None

    def get_income_tax_display(self):
        return f'{self.income_tax:.2f} €' if self.income_tax else None

    def get_nett_income_display(self):
        return f'{self.nett_income:.2f} €' if self.nett_income else None


class Project(TimeStampedModel, ProjectDisplayMixin):
    state = FSMField(default='requested', editable=False)
    state_colors = {
        'requested': '#71b2d4',
        'scoped': '#43b1b0',
        'introduced': '#71b2d4',
        'signed': '#189370',
        'progress': '#43b1b0',
        'finished': '#246060',
        'stopped': '#cd3238'
    }

    @property
    def state_color(self):
        return self.state_colors.get(self.state, '#000')

    @transition(field=state, source='requested', target='scoped', custom={
        'help': 'This project was scoped, on email or call',
    })
    def scope(self):
        pass

    @transition(field=state, source='scoped', target='introduced', custom={
        'help': 'Introduced to the end client',
    })
    def introduce(self):
        pass

    @transition(field=state, source='introduced', target='signed', custom={
        'help': 'Contract signed',
    })
    def sign(self):
        pass

    @transition(field=state, source='signed', target='progress', custom={
        'help': 'Started working',
    })
    def start(self):
        pass

    @transition(field=state, source='progress', target='finished', custom={
        'help': 'Finished working',
    })
    def finish(self):
        pass

    @transition(field=state, source='*', target='stopped', custom={
        'help': 'Project dropped',
        'classes': ['no'],
    })
    def drop(self):
        pass

    name = models.CharField(max_length=120)
    company = models.ForeignKey('Company',
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

    notes = RichTextField(null=True, blank=True)
    daily_rate = models.DecimalField(
        decimal_places=2,
        max_digits=6,
        null=True,
        blank=True
    )
    language = CharField(choices=settings.LANGUAGES, max_length=10, default='en')

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
            InstanceSelectorPanel('company'),
            InstanceSelectorPanel('manager'),
            FieldRowPanel([
                InstanceSelectorPanel('location'),
                FieldPanel('language'),
            ])
        ]),
        FieldRowPanel([
            FieldPanel('daily_rate'),
            FieldPanel('start_date'),
            FieldPanel('end_date')
        ]),
        FieldPanel('notes'),
        PageChooserPanel('project_page')
    ]

    def get_message_template(self, transition_name):
        from crm.models import MessageTemplate
        return MessageTemplate.objects.filter(state_transition=transition_name).first()

    @property
    def duration(self):
        try:
            return math.ceil((self.end_date - self.start_date).days / 30)
        except TypeError:
            pass

    def get_duration_display(self):
        return f'{self.duration} months'

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

    @property
    def logo(self):
        return self.company.logo if self.company else None

    def clean(self):
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError(
                {
                    'start_date': "End date can't be earlier than start date",
                    'end_date': "End date can't be earlier than start date",
                }
            )

    def create_cv(self, user):
        site = Site.objects.get(is_default_site=True)
        cv_settings = CVGenerationSettings.for_site(site)

        return CV.objects.create(
            title=cv_settings.default_title,
            experience_overview=cv_settings.default_experience_overview,
            education_overview=cv_settings.default_education_overview,
            contact_details=cv_settings.default_contact_details,
            languages_overview=cv_settings.default_languages_overview,
            rate_overview=cv_settings.default_rate_overview,
            working_permit=cv_settings.default_working_permit,
            full_name=f'{user.first_name} {user.last_name}',
            picture=cv_settings.default_picture,
            project=self
        )

    def save(self, *args, **kwargs):
        if not self.daily_rate and self.company:
            self.daily_rate = self.company.default_daily_rate
        if not self.name:
            self.name = str(self.company)
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.name or self.company)

    class Meta:
        verbose_name_plural = 'projects'

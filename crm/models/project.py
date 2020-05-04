import math

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.safestring import SafeText
from django_extensions.db.models import TimeStampedModel
from instance_selector.edit_handlers import InstanceSelectorPanel
from wagtail.admin.edit_handlers import MultiFieldPanel, FieldPanel, FieldRowPanel, PageChooserPanel
from wagtail.core.fields import RichTextField
from wagtailmarkdown.fields import MarkdownField
from wagtailmarkdown.utils import render_markdown

from crm.project_states import ProjectStateMixin
from crm.utils import get_working_days


class Project(ProjectStateMixin, TimeStampedModel):
    name = models.CharField(max_length=120,
                            blank=True, null=True)
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
            InstanceSelectorPanel('company'),
            InstanceSelectorPanel('manager'),
        ]),
        FieldRowPanel([
            MultiFieldPanel([
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
    def duration(self):
        try:
            return math.ceil((self.end_date - self.start_date).days / 30)
        except TypeError:
            pass

    def get_duration_display(self):
        return f'{self.duration} months'

    def get_original_description_display(self):
        return SafeText(self.original_description)

    def get_notes_display(self):
        return SafeText(render_markdown(self.notes))

    def get_project_page_display(self):
        if not self.project_page:
            return
        url = reverse('wagtailadmin_pages:edit', args=(self.project_page.pk,))
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
        return f'{self.budget} €' if self.budget else None

    def get_vat_display(self):
        return f'{self.vat:.2f} €' if self.vat else None

    def get_invoice_amount_display(self):
        return f'{self.invoice_amount:.2f} €' if self.invoice_amount else None

    def get_income_tax_display(self):
        return f'{self.income_tax:.2f} €' if self.income_tax else None

    def get_nett_income_display(self):
        return f'{self.nett_income:.2f} €' if self.nett_income else None

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

import math

from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.safestring import SafeText
from django_extensions.db.models import TimeStampedModel
from phonenumber_field.modelfields import PhoneNumberField
from wagtail.core.fields import RichTextField
from wagtailmarkdown.fields import MarkdownField
from wagtailmarkdown.utils import render_markdown

from crm.project_states import ProjectStateMixin
from crm.utils import get_working_days


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

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def project_count(self):
        return self.projects.count()

    class Meta:
        verbose_name_plural = 'people'


class Channel(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField(blank=True,
                          null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'channels'


class Project(ProjectStateMixin, models.Model):
    recruiter = models.ForeignKey('Recruiter',
                                  on_delete=models.CASCADE,
                                  related_name='projects')
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
                                 on_delete=models.CASCADE)

    original_description = RichTextField()
    original_url = models.URLField(null=True, blank=True)

    notes = MarkdownField()
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
        url = reverse("wagtailadmin_pages:edit", args=(self.project_page.pk,))
        return SafeText(
            f"<a href='{url}'>{self.project_page}</a>"
        )

    @property
    def budget(self):
        if not self.start_date or not self.end_date:
            return
        working_days = get_working_days(self.start_date, self.end_date)
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

    def get_budget_display(self):
        return f"{self.budget} €"

    def get_vat_display(self):
        return f"{self.vat:.2f} €"

    def get_invoice_amount_display(self):
        return f"{self.invoice_amount:.2f} €"

    def get_income_tax_display(self):
        return f"{self.income_tax:.2f} €"

    def get_nett_income_display(self):
        return f"{self.nett_income:.2f} €"

    def clean(self):
        if self.start_date >= self.end_date:
            raise ValidationError(
                {
                    "start_date": "End date can't be earlier than start date",
                    "end_date": "End date can't be earlier than start date",
                }
            )

    def save(self, *args, **kwargs):
        if not self.daily_rate and self.recruiter:
            self.daily_rate = self.recruiter.default_daily_rate
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.company) or str(self.recruiter)

    class Meta:
        verbose_name_plural = "projects"


class BaseCompany(TimeStampedModel):
    name = models.CharField(max_length=200,
                            unique=True)
    location = models.ForeignKey('crm.City',
                                 on_delete=models.CASCADE)
    channel = models.ForeignKey('Channel',
                                on_delete=models.SET_NULL,
                                help_text="Lead channel this company came from",
                                null=True,
                                blank=True)
    url = models.URLField(blank=True,
                          null=True)
    notes = MarkdownField(default="", blank=True)

    def __str__(self):
        return self.name

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

    class Meta:
        verbose_name_plural = 'recruiters'


class ClientCompany(BaseCompany):
    pass

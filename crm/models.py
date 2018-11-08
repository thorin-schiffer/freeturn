from django.db import models
from django.conf import settings
from django_extensions.db.models import TimeStampedModel
from phonenumber_field.modelfields import PhoneNumberField
from wagtail.core.fields import RichTextField
from wagtailmarkdown.fields import MarkdownField

from crm.project_states import ProjectStateMixin


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
    project_page = models.ForeignKey('home.ProjectPage',
                                     on_delete=models.SET_NULL,
                                     null=True,
                                     blank=True)

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

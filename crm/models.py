from django.db import models
from django.conf import settings
from django_extensions.db.models import TimeStampedModel
from phonenumber_field.modelfields import PhoneNumberField


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

    company = models.ForeignKey('Company',
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


class Project(models.Model):
    project_page = models.ForeignKey('home.ProjectPage',
                                     on_delete=models.SET_NULL,
                                     null=True,
                                     blank=True)
    company = models.ForeignKey('Company',
                                on_delete=models.CASCADE,
                                related_name='projects')
    manager = models.ForeignKey('Employee',
                                on_delete=models.SET_NULL,
                                null=True,
                                blank=True,
                                related_name='projects')
    location = models.ForeignKey('crm.City',
                                 related_name='projects',
                                 on_delete=models.CASCADE)

    daily_rate = models.DecimalField(
        decimal_places=2,
        max_digits=6,
        null=True,
        blank=True
    )

    def save(self, *args, **kwargs):
        if not self.daily_rate and self.company:
            self.daily_rate = self.company.default_daily_rate
        super().save(*args, **kwargs)

    def __str__(self):
        return self.project_page.title if self.project_page else str(self.company)

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

    class Meta:
        abstract = True


class Company(BaseCompany):
    is_hr = models.BooleanField(default=True)
    default_daily_rate = models.DecimalField(
        decimal_places=2,
        max_digits=6,
        null=True,
        blank=True,
        default=settings.DEFAULT_DAILY_RATE
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'companies'

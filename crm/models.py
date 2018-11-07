from django.db import models

from django_extensions.db.models import TimeStampedModel
from phonenumber_field.modelfields import PhoneNumberField


class City(models.Model):
    name = models.CharField(max_length=200,
                            unique=True)

    @property
    def project_count(self):
        return self.projects.count()

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


class Channel(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField(blank=True,
                          null=True)


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
                                blank=True)
    location = models.ForeignKey('crm.City',
                                 related_name='projects',
                                 on_delete=models.CASCADE)


class Company(TimeStampedModel):
    name = models.CharField(max_length=200,
                            unique=True)
    location = models.ForeignKey('crm.City',
                                 on_delete=models.CASCADE)
    is_hr = models.BooleanField(default=True)
    channel = models.ForeignKey('Channel',
                                on_delete=models.SET_NULL,
                                help_text="Lead channel this company came from",
                                null=True,
                                blank=True)

    class Meta:
        verbose_name_plural = 'companies'

from django.db import models

# Create your models here.
from django_extensions.db.models import TimeStampedModel
from phonenumber_field.modelfields import PhoneNumberField


class City(models.Model):
    name = models.CharField(max_length=200,
                            unique=True)


class Employee(TimeStampedModel):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    telephone = PhoneNumberField(null=True,
                                 blank=True)
    email = models.EmailField()

    company = models.ForeignKey('Company',
                                on_delete=models.CASCADE)


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
                                 on_delete=models.CASCADE)


class Company(TimeStampedModel):
    name = models.CharField(max_length=200,
                            unique=True)
    location = models.ForeignKey('crm.City',
                                 on_delete=models.CASCADE)
    is_hr = models.BooleanField(default=True)

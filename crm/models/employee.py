from django.db import models
from django_extensions.db.models import TimeStampedModel
from instance_selector.edit_handlers import InstanceSelectorPanel
from wagtail.admin.edit_handlers import FieldRowPanel, MultiFieldPanel, FieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel


class Employee(TimeStampedModel):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    telephone = models.CharField(max_length=200,
                                 null=True,
                                 blank=True)
    mobile = models.CharField(max_length=200,
                              null=True,
                              blank=True)

    email = models.EmailField()

    company = models.ForeignKey('Company',
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
                    InstanceSelectorPanel('company'),
                    ImageChooserPanel('picture'),
                ]),
            ]
        ),
    ]

    def __str__(self):
        return f'{self.first_name} {self.last_name} [{self.company}]'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def project_count(self):
        return self.projects.count()

    class Meta:
        verbose_name_plural = 'people'
        ordering = ['-created']

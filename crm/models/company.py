from django.conf import settings
from django.db import models
from django_extensions.db.models import TimeStampedModel
from tld import get_fld
from wagtail.admin.edit_handlers import FieldRowPanel, MultiFieldPanel, FieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtailmarkdown.fields import MarkdownField


class Company(TimeStampedModel):
    name = models.CharField(max_length=200,
                            unique=True)
    location = models.ForeignKey('crm.City',
                                 on_delete=models.CASCADE,
                                 blank=True,
                                 null=True)
    channel = models.ForeignKey('Channel',
                                on_delete=models.SET_NULL,
                                help_text='Lead channel this company came from',
                                null=True,
                                blank=True)
    url = models.URLField(blank=True,
                          null=True)
    notes = MarkdownField(default='', blank=True)
    logo = models.ForeignKey('wagtailimages.Image', on_delete=models.SET_NULL,
                             null=True, blank=True)
    default_daily_rate = models.DecimalField(
        decimal_places=2,
        max_digits=6,
        null=True,
        blank=True,
        default=settings.DEFAULT_DAILY_RATE
    )
    payment_address = MarkdownField(null=True, blank=True)
    vat_id = models.CharField(max_length=100, help_text='VAT ID', null=True, blank=True)

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
        FieldRowPanel([FieldPanel('notes')]),
        FieldPanel('default_daily_rate'),
        FieldRowPanel([
            FieldPanel('payment_address'),
            FieldPanel('vat_id'),
        ]),

    ]

    def __str__(self):
        return self.name

    @property
    def domain(self):
        return get_fld(self.url, fail_silently=True)

    class Meta:
        verbose_name_plural = 'companies'
        verbose_name = 'company'

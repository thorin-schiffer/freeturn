from django.db import models
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.contrib.settings.models import BaseSetting
from wagtail.contrib.settings.registry import register_setting
from wagtail.core.fields import RichTextField
from wagtail.images.edit_handlers import ImageChooserPanel

INVOICE_LANGUAGE_CHOICES = (
    ('en', 'English'),
    ('de', 'German')
)


@register_setting(icon='form')
class InvoiceGenerationSettings(BaseSetting):
    default_title = models.CharField(
        max_length=255, help_text='Default title to use',
        default='Freelance python developer')
    default_language = models.CharField(
        default='en',
        choices=INVOICE_LANGUAGE_CHOICES,
        max_length=4
    )
    default_unit = models.CharField(
        max_length=200,
        default='hour',
        help_text='Work unit'
    )
    default_vat = models.FloatField(
        default=19,
        help_text='VAT in %'
    )

    default_payment_period = models.PositiveIntegerField(
        default=14,
        help_text='Amount of days for this invoice to be payed'
    )

    default_receiver_vat_id = models.CharField(max_length=100, help_text='VAT ID of the receiver (you)')

    default_tax_id = models.CharField(max_length=100, help_text='Your local tax id')

    default_bank_account = RichTextField(help_text='Payment bank account details')
    default_contact_data = RichTextField()

    default_logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    panels = [
        FieldPanel('default_title'),
        FieldPanel('default_language'),
        FieldPanel('default_unit'),
        FieldPanel('default_vat'),
        FieldPanel('default_payment_period'),
        FieldPanel('default_receiver_vat_id'),
        FieldPanel('default_tax_id'),
        FieldPanel('default_bank_account'),
        FieldPanel('default_contact_data'),
        ImageChooserPanel('default_logo')
    ]


@register_setting(icon='cog')
class CVGenerationSettings(BaseSetting):
    default_title = models.CharField(
        max_length=255, help_text='Default title to use', default='Freelance python developer')
    default_experience_overview = RichTextField(
        help_text='Notice on your experience',
        default='Python developer experience: 7 years', blank=True, null=True
    )

    default_education_overview = RichTextField(
        help_text='Notice on your education',
        default='Novosibirsk State Technical University', blank=True, null=True
    )
    default_contact_details = RichTextField(default='thorin@schiffer.pro', blank=True, null=True)
    default_languages_overview = RichTextField(default='English: fluent', blank=True, null=True)
    default_rate_overview = RichTextField(default='100 schmeckles', blank=True, null=True)
    default_working_permit = RichTextField(default='PERMANENT RESIDENCE', blank=True, null=True)
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
        ImageChooserPanel('default_picture')
    ]

from django.db import models
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.contrib.settings.models import BaseSetting
from wagtail.contrib.settings.registry import register_setting
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtailmarkdown.fields import MarkdownField

INVOICE_LANGUAGE_CHOICES = (
    ('en', 'English'),
    ('de', 'German')
)


@register_setting(icon='icon icon-fa-id-card')
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

    default_bank_account = MarkdownField(help_text='Payment bank account details')
    default_contact_data = MarkdownField()

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


@register_setting(icon='icon icon-fa-id-card')
class CVGenerationSettings(BaseSetting):
    default_title = models.CharField(
        max_length=255, help_text='Default title to use', default='Freelance python developer')
    default_experience_overview = MarkdownField(
        help_text='Notice on your experience',
        default='Python developer experience: 7 years'
    )

    default_education_overview = MarkdownField(
        help_text='Notice on your education',
        default='Novosibirsk State Technical University'
    )
    default_contact_details = MarkdownField(default='sergey@cheparev.com')
    default_languages_overview = MarkdownField(default='English: fluent')
    default_rate_overview = MarkdownField(default='<<change default in settings>>')
    default_working_permit = MarkdownField(default='PERMANENT RESIDENCE')
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

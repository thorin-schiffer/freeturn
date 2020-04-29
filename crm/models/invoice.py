import logging
from dataclasses import dataclass, field
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import CASCADE
from django.utils import timezone
from django_extensions.db.models import TimeStampedModel
from wagtail.admin.edit_handlers import FieldPanel, FieldRowPanel, MultiFieldPanel, StreamFieldPanel
from wagtail.contrib.settings.models import BaseSetting
from wagtail.contrib.settings.registry import register_setting
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.core.blocks import StreamValue
from wagtail.core.fields import StreamField
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtailmarkdown.fields import MarkdownField

logger = logging.getLogger('crm.models')
invoice_raw_options = {
    'minSpareRows': 0,
    'rowHeaders': False,
    'contextMenu': False,
    'editor': 'text',
    'stretchH': 'all',
    'height': 216,
    'language': 'en',
    'renderer': 'text',
    'autoColumnSize': False,
    'colHeaders': ['Article', 'Amount units', 'Price per unit'],
    'columns': [
        {'data': 'article'},
        {'data': 'amount', 'type': 'numeric'},
        {'data': 'price', 'type': 'numeric', 'format': '0.00'},
    ]
}


# sometimes positions are lists, sometimes dicts wtf
def dictify_position_row(position):
    if not isinstance(position, dict):
        columns = [column['data'] for column in invoice_raw_options['columns']]
        position = dict(zip(columns, position))
    return position


def regular_positions_stream_data(stream_data):
    # weird that type is changing if the instance is loaded from the db
    if isinstance(stream_data, tuple):
        return stream_data[1]
    elif isinstance(stream_data, dict):
        return stream_data['value']
    else:
        raise ValueError(f'Stream data has unknown type: {stream_data.__class__}, {stream_data}')


INVOICE_LANGUAGE_CHOICES = (
    ('en', 'English'),
    ('de', 'German')
)
INVOICE_CURRENCY_CHOICES = (
    ('€', 'Euro'),
    ('$', 'USD')
)


@dataclass
class InvoicePosition:
    article: str
    amount: int
    price: Decimal = field()
    invoice: 'Invoice'

    @property
    def vat(self):
        return (self.nett_total / 100) * self.invoice.vat

    @property
    def price_with_vat(self):
        return self.price + (self.price * self.invoice.vat) / 100

    @property
    def nett_total(self):
        return self.amount * self.price

    @property
    def total(self):
        return self.nett_total + self.vat


class Invoice(TimeStampedModel):
    project = models.ForeignKey('Project',
                                on_delete=CASCADE,
                                related_name='invoices')

    language = models.CharField(
        default='en',
        choices=INVOICE_LANGUAGE_CHOICES,
        max_length=4
    )

    currency = models.CharField(
        default='€',
        choices=INVOICE_CURRENCY_CHOICES,
        max_length=4
    )

    unit = models.CharField(
        max_length=200,
        default='hours',
        help_text='Work unit'
    )

    vat = models.DecimalField(
        default=settings.DEFAULT_VAT,
        help_text='VAT in %',
        decimal_places=2,
        max_digits=4
    )

    invoice_number = models.CharField(
        max_length=20, unique=True
    )

    payment_period = models.PositiveIntegerField(
        default=14,
        help_text='Amount of days for this invoice to be payed'
    )

    payment_address = MarkdownField(help_text='Copied from the company, if empty', blank=True)

    receiver_vat_id = models.CharField(max_length=100, help_text='VAT ID of the receiver (you)')
    sender_vat_id = models.CharField(max_length=100, help_text='VAT ID of the sender (client), '
                                                               'copied from the company if empty', blank=True)

    issued_date = models.DateField()
    delivery_date = models.DateField()

    tax_id = models.CharField(max_length=100, help_text='Your local tax id')

    bank_account = MarkdownField(help_text='Payment bank account details')
    contact_data = MarkdownField()

    title = models.CharField(max_length=200,
                             default='Python development')

    positions = StreamField([
        ('positions', TableBlock(table_options=invoice_raw_options))
    ])
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Picture to use'
    )
    payed = models.BooleanField(default=False)
    panels = [
        FieldPanel('project'),
        FieldRowPanel([
            FieldPanel('title'),
            FieldPanel('invoice_number'),
        ]),
        FieldRowPanel([
            MultiFieldPanel([
                FieldPanel('payment_address'),
                FieldPanel('issued_date'),
                FieldPanel('delivery_date'),
                FieldPanel('payment_period'),
            ]),
            MultiFieldPanel([
                ImageChooserPanel('logo'),
                FieldPanel('language'),
                FieldPanel('unit'),
                FieldPanel('vat'),
                FieldPanel('tax_id'),
                FieldPanel('receiver_vat_id'),
                FieldPanel('sender_vat_id'),
                FieldPanel('currency')
            ]),
        ]),
        StreamFieldPanel('positions'),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('bank_account'),
                FieldPanel('contact_data'),
            ]),
            FieldPanel('payed')
        ])
    ]

    @property
    def total(self):
        return sum(
            position.total for position in self.invoice_positions
        )

    @property
    def nett_total(self):
        return sum(
            position.nett_total for position in self.invoice_positions
        )

    @property
    def total_vat(self):
        return sum(
            position.vat for position in self.invoice_positions
        )

    @property
    def payable_to(self):
        return self.issued_date + timedelta(days=self.payment_period)

    @property
    def company(self):
        if self.project:
            return self.project.company if self.project.company else self.project.manager.company

    @staticmethod
    def get_next_invoice_number():
        this_year = timezone.now().year
        count_this_year = Invoice.objects.filter(issued_date__year=this_year).count()
        return f'{this_year}-{count_this_year + 1:02d}'

    def copy_company_params(self):
        if self.project.manager:
            payment_address = self.project.manager.company.payment_address
            vat_id = self.project.manager.company.vat_id
        else:
            payment_address = self.project.company.payment_address
            vat_id = self.project.company.vat_id
        self.payment_address = payment_address or ''
        self.sender_vat_id = vat_id or ''

    @staticmethod
    def get_initial_positions():
        table = [
            {
                'article': 'Python programming',
                'amount': settings.DEFAULT_DAILY_RATE,
                'price': f'{settings.DEFAULT_DAILY_RATE / 8:.2f}',
            },
        ]
        return {
            'data': table,
            'first_row_is_table_header': False,
            'first_col_is_header': False
        }

    @property
    def invoice_positions(self):
        positions = []
        for stream_data in self.positions.stream_data:
            stream_data = regular_positions_stream_data(stream_data)

            if not stream_data:
                continue

            for position in stream_data['data']:
                position = dictify_position_row(position)
                if not all(value for value in position.values()):
                    logger.info(f'Skipped not full position: {position}')
                    continue
                positions.append(InvoicePosition(invoice=self,
                                                 price=Decimal(position['price']),
                                                 amount=position['amount'],
                                                 article=position['article']))
        return positions

    def ensure_positions_labels(self):
        # positions are somehow switch from list of lists to dict of lists

        for stream_data in self.positions.stream_data:
            stream_data = regular_positions_stream_data(stream_data)
            if not stream_data:
                continue

            for i, position in enumerate(stream_data['data']):
                stream_data['data'][i] = dictify_position_row(position)

    def __str__(self):
        return f'{self.project}: #{self.invoice_number}'

    def save(self, **kwargs):
        if not self.payment_address and self.project:
            self.copy_company_params()

        if not self.invoice_number:
            self.invoice_number = Invoice.get_next_invoice_number()
        super().save(**kwargs)


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


def wrap_table_data(data):
    original_steam_block = StreamField([('positions', TableBlock(table_options=invoice_raw_options))]).stream_block
    return StreamValue(original_steam_block, [('positions', data)])

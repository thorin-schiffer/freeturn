import logging
import math
from dataclasses import dataclass, field
from datetime import timedelta
from decimal import Decimal

from ajax_select.fields import AutoCompleteSelectMultipleWidget, AutoCompleteSelectWidget
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import CASCADE
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import SafeText
from django_extensions.db.models import TimeStampedModel
from tld import get_fld
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, FieldRowPanel, PageChooserPanel, StreamFieldPanel
from wagtail.contrib.settings.models import BaseSetting
from wagtail.contrib.settings.registry import register_setting
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.core.blocks import StreamValue
from wagtail.core.fields import RichTextField, StreamField
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtailautocomplete.edit_handlers import AutocompletePanel
from wagtailmarkdown.fields import MarkdownField
from wagtailmarkdown.utils import render_markdown

from crm.project_states import ProjectStateMixin
from crm.utils import get_working_days
from home.models import Technology, ProjectPage

logger = logging.getLogger('crm.models')


class City(models.Model):
    name = models.CharField(max_length=200,
                            unique=True)

    @property
    def project_count(self):
        return self.projects.count()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'city'
        ordering = ['name']


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
                    FieldPanel('company', widget=AutoCompleteSelectWidget('companies')),
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


class Channel(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField(blank=True,
                          null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'channels'


class Project(ProjectStateMixin, TimeStampedModel):
    name = models.CharField(max_length=120,
                            blank=True, null=True)
    company = models.ForeignKey('Company',
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
                                 null=True, blank=True,
                                 on_delete=models.CASCADE)

    original_description = RichTextField()
    original_url = models.URLField(null=True, blank=True)

    notes = MarkdownField(null=True, blank=True)
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

    panels = [
        MultiFieldPanel([
            FieldPanel('name'),
            FieldPanel('original_url'),
            FieldPanel('original_description'),

        ]),
        FieldRowPanel([
            MultiFieldPanel([
                FieldPanel('company', widget=AutoCompleteSelectWidget('companies')),
                FieldPanel('manager'),
                FieldPanel('location')
            ]),
            MultiFieldPanel([
                FieldPanel('daily_rate'),
                FieldPanel('start_date'),
                FieldPanel('end_date')
            ])
        ]),
        FieldPanel('notes'),
        PageChooserPanel('project_page')
    ]

    @property
    def duration(self):
        try:
            return math.ceil((self.end_date - self.start_date).days / 30)
        except TypeError:
            pass

    def get_duration_display(self):
        return f'{self.duration} months'

    def get_original_description_display(self):
        return SafeText(self.original_description)

    def get_notes_display(self):
        return SafeText(render_markdown(self.notes))

    def get_project_page_display(self):
        if not self.project_page:
            return
        url = reverse('wagtailadmin_pages:edit', args=(self.project_page.pk,))
        return SafeText(
            f"<a href='{url}'>{self.project_page}</a>"
        )

    @property
    def budget(self):
        if not self.start_date or not self.end_date:
            return
        working_days = len(get_working_days(self.start_date, self.end_date))
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

    @property
    def working_days(self):
        if not self.start_date or not self.end_date:
            return
        return len(get_working_days(self.start_date, self.end_date))

    def get_budget_display(self):
        return f'{self.budget} €' if self.budget else None

    def get_vat_display(self):
        return f'{self.vat:.2f} €' if self.vat else None

    def get_invoice_amount_display(self):
        return f'{self.invoice_amount:.2f} €' if self.invoice_amount else None

    def get_income_tax_display(self):
        return f'{self.income_tax:.2f} €' if self.income_tax else None

    def get_nett_income_display(self):
        return f'{self.nett_income:.2f} €' if self.nett_income else None

    @property
    def logo(self):
        return self.company.logo if self.company else None

    def clean(self):
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError(
                {
                    'start_date': "End date can't be earlier than start date",
                    'end_date': "End date can't be earlier than start date",
                }
            )

    def save(self, *args, **kwargs):
        if not self.daily_rate and self.company:
            self.daily_rate = self.company.default_daily_rate
        if not self.name:
            self.name = str(self.company)
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.name or self.company)

    class Meta:
        verbose_name_plural = 'projects'


class ProjectMessage(TimeStampedModel):
    project = models.ForeignKey('Project',
                                null=True,
                                blank=True,
                                on_delete=models.SET_NULL,
                                related_name='messages')
    author = models.ForeignKey('Employee',
                               on_delete=models.CASCADE,
                               related_name='messages')
    sent_at = models.DateTimeField(default=timezone.now,
                                   help_text='Sending time')
    subject = models.CharField(max_length=200,
                               blank=True,
                               null=True)
    text = models.TextField()

    gmail_message_id = models.CharField(max_length=50)
    gmail_thread_id = models.CharField(max_length=50)

    def __str__(self):
        return str(self.subject)


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


class CV(TimeStampedModel):
    project = models.ForeignKey('Project',
                                blank=True,
                                null=True,
                                on_delete=CASCADE,
                                related_name='cvs')
    earliest_available = models.DateField(null=True, blank=True, default=timezone.now)
    picture = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Picture to use'
    )

    full_name = models.CharField(max_length=200,
                                 help_text='Name to use in the title of the file, default is current user')
    title = models.CharField(max_length=200, help_text='Title to be placed under the name')
    experience_overview = MarkdownField(
        help_text='Notice on your experience',
    )

    relevant_project_pages = models.ManyToManyField(
        'home.ProjectPage',
        help_text='Project pages to be placed on the first page, eye catcher for this project',
        related_name='applications_highlighted',
        blank=True
    )
    include_portfolio = models.BooleanField(
        default=True,
        help_text="Include portfolio projects' description"
    )
    relevant_skills = models.ManyToManyField(
        'home.Technology',
        help_text='Technologies to be included, '
                  'will be automatically formed to look relevant',
        blank=True
    )

    education_overview = MarkdownField(
        help_text='Notice on your education',
    )
    contact_details = MarkdownField()
    languages_overview = MarkdownField()
    rate_overview = MarkdownField(blank=True, null=True)
    working_permit = MarkdownField()

    create_panels = [
        FieldPanel('project'),
        FieldRowPanel(
            [
                MultiFieldPanel(
                    [
                        FieldPanel('full_name'),
                        FieldPanel('title'),
                        FieldPanel('earliest_available'),
                        FieldPanel('experience_overview'),
                        FieldPanel('education_overview'),
                    ],
                    heading='Header data'
                ),
                MultiFieldPanel(
                    [
                        ImageChooserPanel('picture'),
                        FieldPanel('contact_details'),
                        FieldPanel('languages_overview'),
                        FieldPanel('rate_overview'),
                        FieldPanel('working_permit'),
                    ]
                )

            ]
        ),
    ]
    panels = [
        MultiFieldPanel([
            AutocompletePanel('relevant_project_pages', is_single=False,
                              page_type='home.ProjectPage'),
            FieldPanel('include_portfolio'),

        ]),
        FieldPanel('relevant_skills',
                   widget=AutoCompleteSelectMultipleWidget('technologies')),
    ] + create_panels

    @property
    def logo(self):
        return self.project.logo if self.project else None

    def set_relevant_skills_and_projects(self, limit=5):
        technologies = Technology.match_text(self.project.original_description)
        if self.relevant_project_pages.count():
            logger.error(f"Won't set relevant project pages for {self}, it's not empty")
            return
        self.relevant_project_pages.set(ProjectPage.objects.live().filter(
            technologies__in=technologies
        ).order_by('-start_date')[:limit])
        self.relevant_skills.set(technologies)

    def save(self, **kwargs):
        creating = self.pk is None
        super().save(**kwargs)
        if creating and self.project:
            self.set_relevant_skills_and_projects()

    def __str__(self):
        return str(self.project)

    class Meta:
        verbose_name = 'CV'


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

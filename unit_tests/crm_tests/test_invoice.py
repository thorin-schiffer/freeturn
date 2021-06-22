import pytest
from django.urls import reverse
from django.utils import timezone
from webtest import Field

from crm.models.invoice import Invoice
from crm.models.settings import InvoiceGenerationSettings

positions_data = {
    'positions-count': ['1'],
    'positions-0-deleted': [''],
    'positions-0-order': ['0'],
    'positions-0-type': ['positions'], 'positions-0-id': ['da89579e-c58a-4eaa-a1f6-b6532d2ae98c'],
    'handsontable-col-caption': [''], 'positions-0-value': [
        '{"data":[{"article":"Python programming","amount":100,"price":15}],'
        '"cell":[{"row":0,"col":1,"className":"htRight htNumeric"},'
        '{"row":0,"col":2,"className":"htRight htNumeric"}],'
        '"first_row_is_table_header":false,'
        '"first_col_is_header":false,"table_caption":""}'
    ]
}


# stream fields are now done in frontend
# https://docs.wagtail.io/en/stable/releases/2.13.html#streamfield-performance-and-functionality-updates
def add_position_fields(form):
    for name, value in positions_data.items():
        field = Field(form, tag='input', value=value, name=name, pos=20)
        form.fields[name] = [field]
        form.field_order.append((name, field))


@pytest.mark.django_db
def test_create(admin_app, admin_user, default_site, image):
    settings = InvoiceGenerationSettings.for_site(default_site)
    settings.default_logo = image
    settings.save()
    url = f"{reverse('crm_invoice_modeladmin_create')}"

    r = admin_app.get(url)
    form = r.forms[1]

    assert form['title'].value == settings.default_title
    assert form['language'].value == settings.default_language
    assert form['unit'].value == settings.default_unit
    assert float(form['vat'].value) == settings.default_vat
    assert int(form['payment_period'].value) == settings.default_payment_period
    assert form['receiver_vat_id'].value == settings.default_receiver_vat_id
    assert form['tax_id'].value == settings.default_tax_id
    assert settings.default_bank_account in form['bank_account'].value
    assert settings.default_contact_data in form['contact_data'].value
    assert form['logo'].value == str(settings.default_logo.id)
    assert form['issued_date'].value == str(timezone.now().date())
    assert form['delivery_date'].value == str(timezone.now().date())
    assert form['invoice_number'].value == Invoice.get_next_invoice_number()

    add_position_fields(form)
    form.submit()


@pytest.mark.django_db
def test_inspect(admin_app, invoice):
    url = reverse('crm_invoice_modeladmin_inspect', kwargs={'instance_pk': invoice.pk})
    admin_app.get(url)


@pytest.mark.django_db
def test_copy(admin_app, invoice, default_site):
    url = f"{reverse('crm_invoice_modeladmin_create')}?from_instance={invoice.pk}"

    r = admin_app.get(url)
    form = r.forms[1]

    assert form['title'].value == invoice.title
    assert form['language'].value == str(invoice.language)
    assert form['unit'].value == invoice.unit
    assert float(form['vat'].value) == invoice.vat
    assert int(form['payment_period'].value) == invoice.payment_period
    assert form['receiver_vat_id'].value == invoice.receiver_vat_id
    assert form['tax_id'].value == invoice.tax_id
    assert invoice.bank_account in form['bank_account'].value
    assert invoice.contact_data in form['contact_data'].value
    assert form['logo'].value == str(invoice.logo.id)
    assert form['issued_date'].value == str(timezone.now().date())
    assert form['delivery_date'].value == str(timezone.now().date())
    new_invoice_number = Invoice.get_next_invoice_number()
    assert form['invoice_number'].value == new_invoice_number
    assert form['project'].value == str(invoice.project.pk)
    assert form['currency'].value == invoice.currency

    # positions is a fieldset
    add_position_fields(form)
    form.submit()

    assert Invoice.objects.filter(invoice_number=new_invoice_number).exists()


@pytest.mark.django_db
def test_edit(admin_app, invoice):
    url = reverse('crm_invoice_modeladmin_edit', kwargs={'instance_pk': invoice.pk})
    r = admin_app.get(url)
    form = r.forms[1]

    form['title'] = 'test title'
    add_position_fields(form)
    form.submit()

    invoice.refresh_from_db()
    assert invoice.title == 'test title'

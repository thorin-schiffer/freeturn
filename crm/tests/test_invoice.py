import json
from decimal import Decimal

import pytest
from django.urls import reverse
from django.utils import timezone

from crm.models import InvoiceGenerationSettings, Invoice


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
    assert form['bank_account'].value == settings.default_bank_account
    assert form['contact_data'].value == settings.default_contact_data
    assert form['logo'].value == str(settings.default_logo.id)
    assert form['issued_date'].value == str(timezone.now().date())
    assert form['delivery_date'].value == str(timezone.now().date())
    assert form['invoice_number'].value == Invoice.get_next_invoice_number()
    # positions is a fieldset
    positions = json.loads(form['positions-0-value'].value)['data'][0]
    assert positions['amount']
    assert positions['price']
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
    assert form['bank_account'].value == invoice.bank_account
    assert form['contact_data'].value == invoice.contact_data
    assert form['logo'].value == str(invoice.logo.id)
    assert form['issued_date'].value == str(timezone.now().date())
    assert form['delivery_date'].value == str(timezone.now().date())
    new_invoice_number = Invoice.get_next_invoice_number()
    assert form['invoice_number'].value == new_invoice_number
    assert form['project'].value == str(invoice.project.pk)

    # positions is a fieldset
    positions = json.loads(form['positions-0-value'].value)['data'][0]
    assert positions['amount'] == invoice.invoice_positions[0].amount
    assert Decimal(positions['price']) == invoice.invoice_positions[0].price

    form.submit()

    assert Invoice.objects.filter(invoice_number=new_invoice_number).exists()

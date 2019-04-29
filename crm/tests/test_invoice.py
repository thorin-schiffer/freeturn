import pytest
from django.urls import reverse
from django.utils import timezone

from crm.models import InvoiceGenerationSettings


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
    form.submit()

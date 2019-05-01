from django.utils import timezone
from wagtail.contrib.modeladmin.options import ModelAdmin
from wagtail.contrib.modeladmin.views import CreateView
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.core.blocks import StreamValue
from wagtail.core.fields import StreamField

from crm.models import Invoice, InvoiceGenerationSettings, invoice_raw_options


def wrap_table_data(data):
    original_steam_block = StreamField([('positions', TableBlock(table_options=invoice_raw_options))]).stream_block
    return StreamValue(original_steam_block, [('positions', data)])


class CreateInvoiceView(CreateView):
    def get_initial(self):
        site = self.request.site
        settings = InvoiceGenerationSettings.for_site(site)

        return {
            "title": settings.default_title,
            "language": settings.default_language,
            "unit": settings.default_unit,
            "vat": settings.default_vat,
            "payment_period": settings.default_payment_period,
            "receiver_vat_id": settings.default_receiver_vat_id,
            "tax_id": settings.default_tax_id,
            "bank_account": settings.default_bank_account,
            "contact_data": settings.default_contact_data,
            "logo": settings.default_logo,
            "issued_date": timezone.now().date(),
            "delivery_date": timezone.now().date(),
            "invoice_number": Invoice.get_next_invoice_number(),
            "positions": wrap_table_data(Invoice.get_initial_positions())
        }


class InvoiceAdmin(ModelAdmin):
    model = Invoice
    menu_icon = 'fa-file'
    menu_label = 'Invoices'
    list_display = ['project', 'created']
    list_filter = ['project', 'created']
    list_per_page = 10
    list_select_related = ['project']
    ordering = ['-created']
    inspect_view_enabled = True
    list_display_add_buttons = 'project'
    create_view_class = CreateInvoiceView

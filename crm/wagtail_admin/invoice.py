from django.utils import timezone
from wagtail.contrib.modeladmin.options import ModelAdmin
from wagtail.contrib.modeladmin.views import CreateView, InspectView
from wkhtmltopdf.views import PDFTemplateView

from crm.models import Invoice, InvoiceGenerationSettings, wrap_table_data


class InvoiceCreateView(CreateView):
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


class InvoiceInspectView(PDFTemplateView,
                         InspectView):
    show_content_in_browser = True
    template_name = "invoice.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def get_filename(self):
        return f"{self.instance}.pdf"


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
    create_view_class = InvoiceCreateView
    inspect_view_class = InvoiceInspectView
    inspect_template_name = InvoiceInspectView.template_name

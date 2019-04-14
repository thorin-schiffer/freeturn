from wagtail.contrib.modeladmin.options import ModelAdmin
from wagtail.contrib.modeladmin.views import CreateView

from crm.models import Invoice, InvoiceGenerationSettings


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
            "logo": settings.default_logo
        }


class InvoiceAdmin(ModelAdmin):
    model = Invoice
    menu_icon = 'fa-file'
    menu_label = 'Invoices'
    list_display = ['admin_thumb', 'project', 'created']
    list_filter = ['project', 'created']
    list_per_page = 10
    list_select_related = ['project']
    ordering = ['-created']
    inspect_view_enabled = True
    list_display_add_buttons = 'project'
    create_view_class = CreateInvoiceView

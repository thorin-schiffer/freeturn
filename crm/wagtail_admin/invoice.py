from django.contrib.admin.utils import quote
from django.utils import timezone
from django.utils import translation
from wagtail.contrib.modeladmin.helpers import ButtonHelper, AdminURLHelper
from wagtail.contrib.modeladmin.options import ModelAdmin
from wagtail.contrib.modeladmin.views import CreateView, InspectView, EditView

from crm.models import Invoice, InvoiceGenerationSettings, wrap_table_data
from crm.utils import BasePDFView


class InvoiceCreateView(CreateView):
    def get_default(self):
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

    def from_instance(self, instance: Invoice):
        return {
            "title": instance.title,
            "language": instance.language,
            "unit": instance.unit,
            "vat": instance.vat,
            "payment_period": instance.payment_period,
            "receiver_vat_id": instance.receiver_vat_id,
            "tax_id": instance.tax_id,
            "bank_account": instance.bank_account,
            "contact_data": instance.contact_data,
            "logo": instance.logo,
            "issued_date": timezone.now().date(),
            "delivery_date": timezone.now().date(),
            "invoice_number": Invoice.get_next_invoice_number(),
            "positions": instance.positions,
            "project": instance.project,
            "currency": instance.currency
        }

    def get_initial(self):
        from_instance = self.request.GET.get('from_instance')
        if from_instance:
            try:
                from_instance = Invoice.objects.filter(pk=from_instance).first()
            except ValueError:
                from_instance = None
            return self.from_instance(from_instance)
        return self.get_default()


class InvoiceInspectView(BasePDFView,
                         InspectView):
    show_content_in_browser = True
    template_name = "invoice.html"

    def get_filename(self):
        return f"{self.instance}.pdf"

    def get(self, request, *args, **kwargs):
        request.LANGUAGE_CODE = self.instance.language
        translation.activate(self.instance.language)
        return super().get(request, *args, **kwargs)


class InvoiceEditView(EditView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.ensure_positions_labels()


class InvoiceURLHelper(AdminURLHelper):
    pass


class InvoiceButtonHelper(ButtonHelper):
    def get_buttons_for_obj(self, obj, *args, **kwargs):
        btns = super().get_buttons_for_obj(obj, *args, **kwargs)
        usr = self.request.user
        ph = self.permission_helper
        pk = getattr(obj, self.opts.pk.attname)

        if ph.user_can_edit_obj(usr, obj):
            btns.append(
                {
                    'url': f"{self.url_helper.get_action_url('create')}?from_instance={quote(pk)}",
                    'label': "Copy",
                    'classname': self.finalise_classname(['button-small']),
                    'title': "Copy this invoice, invoice number will be increased",
                }
            )
        return btns


class InvoiceAdmin(ModelAdmin):
    model = Invoice
    menu_icon = 'fa-file'
    menu_label = 'Invoices'
    list_display = ['invoice_number', 'project', 'company', 'created', 'payed', 'payable_to']
    list_filter = ['project', 'created']
    list_per_page = 10
    list_select_related = ['project']
    ordering = ['-created']
    inspect_view_enabled = True
    list_display_add_buttons = 'invoice_number'
    create_view_class = InvoiceCreateView
    inspect_view_class = InvoiceInspectView
    inspect_template_name = InvoiceInspectView.template_name
    edit_view_class = InvoiceEditView
    button_helper_class = InvoiceButtonHelper

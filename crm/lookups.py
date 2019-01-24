from ajax_select import register, LookupChannel

from crm.models import ClientCompany


@register('companies')
class CompanyLookup(LookupChannel):
    model = ClientCompany

    def get_query(self, q, request):
        return self.model.objects.filter(name__icontains=q)

    def format_item_display(self, item):
        return u"<span class='icon icon-fa-user-circle'>%s</span>" % item.name

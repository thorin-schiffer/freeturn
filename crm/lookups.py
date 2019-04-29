from ajax_select import register, LookupChannel

from crm.models import Recruiter


@register('recruiters')
class RecruiterLookup(LookupChannel):
    model = Recruiter

    def get_query(self, q, request):
        return self.model.objects.filter(name__icontains=q)

    def format_item_display(self, item):
        return u"<span class='icon icon-fa-user-building'>%s</span>" % item.name

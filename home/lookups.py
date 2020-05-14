from ajax_select import register, LookupChannel

from home.models.snippets import Technology


@register('technologies')
class TechnologiesLookup(LookupChannel):
    model = Technology

    def get_query(self, q, request):
        return self.model.objects.filter(name__icontains=q)

    def format_item_display(self, item):
        return "<span class='icon icon-fa-cog'>%s</span>" % item.name

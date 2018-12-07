from ajax_select import register, LookupChannel
from taggit.models import Tag


@register('technologies')
class TagsLookup(LookupChannel):
    model = Tag

    def get_query(self, q, request):
        return self.model.objects.filter(name=q).exclude(info=None)

    def format_item_display(self, item):
        return u"<span class='tagit-label tag'>%s</span>" % item.name

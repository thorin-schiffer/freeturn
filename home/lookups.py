from ajax_select import register, LookupChannel
from taggit.models import Tag

from home.models import ProjectPage


@register('technologies')
class TagsLookup(LookupChannel):
    model = Tag

    def get_query(self, q, request):
        return self.model.objects.filter(name__icontains=q).exclude(info=None)

    def format_item_display(self, item):
        return u"<span class='tagit-label tag'>%s</span>" % item.name


@register('project_pages')
class ProjectPageLookup(LookupChannel):
    model = ProjectPage

    def get_query(self, q, request):
        return self.model.objects.live().filter(title__icontains=q)

    def format_item_display(self, item):
        return u"<span class='icon icon-fa-product-hunt'>%s</span>" % item.title

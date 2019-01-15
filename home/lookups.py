from ajax_select import register, LookupChannel
from home.models import ProjectPage, TechnologyInfo


@register('technologies')
class TechnologiesLookup(LookupChannel):
    model = TechnologyInfo

    def get_query(self, q, request):
        return self.model.objects.filter(name__icontains=q)

    def format_item_display(self, item):
        return u"<span class='icon icon-fa-cog'>%s</span>" % item.name


@register('project_pages')
class ProjectPageLookup(LookupChannel):
    model = ProjectPage

    def get_query(self, q, request):
        return self.model.objects.live().filter(title__icontains=q)

    def format_item_display(self, item):
        return u"<span class='icon icon-fa-product-hunt'>%s</span>" % item.title

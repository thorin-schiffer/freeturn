from django.utils.safestring import mark_safe
from social_core.exceptions import AuthForbidden
from django.utils.html import format_html
from wagtail.admin.edit_handlers import EditHandler


def social_for_authed_only(backend, *args, **kwargs):
    request = kwargs.get('request')
    if not request or not request.user.is_authenticated:
        raise AuthForbidden(backend)


def result_pks(response, cast=None):
    """
    returns ids from wagtail admin search result
    :param cast: cast pks to a type, default int
    :param response: webtest response
    :return: ids list
    """
    cast = cast or int
    result_rows = response.lxml.xpath('.//tr[@data-object-pk]/@data-object-pk')
    return [
        cast(r) for r in result_rows
    ]


def required_inputs(response):
    inputs = response.lxml.xpath('.//*[@required]/@id')
    return [
        i.replace('id_', '') for i in inputs
    ]


def disabled_in_admin(func):
    """
    returns empty dict instead of actual context processor in admin
    """

    def _inner(request):
        if request.path.startswith('/admin/'):
            return {}
        return func(request)

    return _inner


def get_messages(r):
    messages = [
        (m.get('class'), m.xpath('./text()')[1].strip()) for m in r.lxml.xpath(".//div[@class='messages']//li")
    ]
    return messages


class ReadOnlyPanel(EditHandler):
    def __init__(self, attr, *args, **kwargs):
        self.attr = attr
        super().__init__(*args, **kwargs)

    def clone(self):
        return self.__class__(
            attr=self.attr,
            heading=self.heading,
            classname=self.classname,
            help_text=self.help_text,
        )

    def render(self):
        value = getattr(self.instance, self.attr)
        if callable(value):
            value = value()
        return format_html('<div>{}</div>', mark_safe(value))

    def render_as_object(self):
        return format_html(
            '<fieldset><legend>{}</legend>'
            '<ul class="fields"><li><div class="field">{}</div></li></ul>'
            '</fieldset>',
            self.heading, self.render())

    def render_as_field(self):
        return format_html(f'<label>{self.heading}:</label> <div class="field_content">{self.render()}</div>')

from social_core.exceptions import AuthForbidden


def social_for_authed_only(backend, details, response, *args, **kwargs):
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
    result_rows = response.lxml.xpath(".//tr[@data-object-pk]/@data-object-pk")
    return [
        cast(r) for r in result_rows
    ]


def required_inputs(response):
    inputs = response.lxml.xpath(".//*[@required]/@id")
    return [
        i.replace("id_", "") for i in inputs
    ]

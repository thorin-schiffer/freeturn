from social_core.exceptions import AuthForbidden


def social_for_authed_only(backend, details, response, *args, **kwargs):
    request = kwargs.get('request')
    if not request or not request.user.is_authenticated:
        raise AuthForbidden(backend)

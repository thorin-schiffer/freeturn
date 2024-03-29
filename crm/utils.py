from datetime import datetime
from datetime import timedelta

import holidays
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials as GoogleCredentials
from requests import exceptions as requests_errors
from social_django.utils import load_strategy
from wkhtmltopdf.views import PDFTemplateView

from freeturn import settings


def get_working_days(start_date, end_date):
    days = [start_date + timedelta(days=1) * i for i in range(
        (end_date - start_date).days + 1
    )]

    working_days = []
    for day in days:
        if day in holidays.DE(prov='BE') or day.weekday() in [5, 6]:
            continue
        working_days.append(day)
    return working_days


# https://github.com/python-social-auth/social-core/issues/125#issuecomment-389070863
class Credentials(GoogleCredentials):
    """Google auth credentials using python social auth under the hood"""

    def _parse_expiry(self, data):
        """
        Parses the expiry field from a data into a datetime.

        Args:
             data (Mapping): extra_data from UserSocialAuth model
        Returns:
             datetime: The expiration
        """
        return datetime.now() + timedelta(seconds=data['expires'])

    def __init__(self, usa):
        """
        Args:
            usa (UserSocialAuth): UserSocialAuth google-oauth2 object
        """
        backend = usa.get_backend_instance(load_strategy())
        data = usa.extra_data
        token = data['access_token']
        refresh_token = data['refresh_token']
        token_uri = backend.refresh_token_url()
        client_id, client_secret = backend.get_key_and_secret()
        scopes = backend.get_scope()
        # id_token is not provided with GoogleOAuth2 backend
        super().__init__(
            token, refresh_token=refresh_token, id_token=None,
            token_uri=token_uri, client_id=client_id, client_secret=client_secret,
            scopes=scopes
        )
        self.usa = usa
        # Needed for self.expired() check
        self.expiry = self._parse_expiry(data)

    def refresh(self, request):
        """Refreshes the access token.

        Args:
            request (google.auth.transport.Request): The object used to make
                HTTP requests.

        Raises:
            google.auth.exceptions.RefreshError: If the credentials could
                not be refreshed.
        """
        usa = self.usa
        try:
            usa.refresh_token(load_strategy())
        except requests_errors.HTTPError as e:
            raise RefreshError(e)
        data = usa.extra_data
        self.token = data['access_token']
        self._refresh_token = data['refresh_token']
        self.expiry = self._parse_expiry(data)


class BasePDFView(PDFTemplateView):
    show_content_in_browser = True

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'load_styles': not settings.TESTING
        }

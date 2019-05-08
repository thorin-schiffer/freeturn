from google.oauth2.credentials import Credentials
from googleapiclient.http import HttpMock

from crm.gmail_utils import get_raw_messages


def test_get_raw_messages():
    creds = Credentials("xyz")
    # https://developers.google.com/api-client-library/python/guide/mocks
    http = HttpMock('books-discovery.json', {'status': '200'})
    get_raw_messages(creds, http)

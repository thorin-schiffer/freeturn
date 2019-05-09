import json
import os

import pytest

from crm.gmail_utils import get_raw_messages


@pytest.fixture
def gmail_service(mock):
    service = mock.Mock()
    from django.conf import settings
    path = os.path.join(
        settings.BASE_DIR, "crm", "tests", "data", "gmapi_labels_response.json"
    )
    with open(path, "r") as f:
        data = json.load(f)
    mock.patch('crm.gmail_utils.get_labels', lambda s: data)
    return service


def test_get_raw_messages(gmail_service):
    get_raw_messages(gmail_service)

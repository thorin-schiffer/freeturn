import json
from datetime import date

import pytest

from crm.gmail_utils import parse_message


@pytest.fixture
def gmail_api_message():
    with open("data/gmail_api_message.json", "r") as f:
        return json.load(f)


def test_parse_message(gmail_api_message):
    result = parse_message(gmail_api_message)
    assert result['sent_at'].date() == date(2019, 1, 26)
    assert result['text'].strip() == "this is *test *email"
    assert result['subject'] == "Test email"
    assert result['from_address'] == "sergey@cheparev.com"
    assert result['gmail_message_id'] == "1688b0102744bab7"
    assert result['gmail_thread_id'] == "1688b00c9ec9d5e7"


def test_save_message():
    raise NotImplementedError()

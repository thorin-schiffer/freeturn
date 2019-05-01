import json
import os
import uuid
from datetime import date
from datetime import timedelta
from email.message import Message as EmailMessage

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from crm.gmail_utils import parse_message, associate, remove_quotation
from home.models import Technology


@pytest.mark.django_db
def test_clean(project):
    project.start_date = timezone.now()
    project.end_date = project.start_date - timedelta(days=1)
    with pytest.raises(ValidationError):
        project.clean()

    project.end_date = project.start_date + timedelta(days=1)
    project.clean()


@pytest.mark.django_db
def test_projects_count(city, employee, project_factory):
    project_factory.create(location=city, manager=employee)
    assert city.project_count == 1
    assert employee.project_count == 1


@pytest.mark.django_db
def test_project_duration(project):
    project.start_date = date(2018, 11, 26)
    project.end_date = date(2018, 12, 30)
    assert project.duration == 2

    project.start_date = None
    assert project.duration is None


@pytest.fixture
def gmail_api_message():
    from django.conf import settings
    path = os.path.join(
        settings.BASE_DIR, "crm", "tests", "data", "gmail_api_message.json"
    )
    with open(path, "r") as f:
        return json.load(f)


def test_parse_message(gmail_api_message):
    result = parse_message(gmail_api_message)
    assert result['sent_at'].date() == date(2019, 1, 26)
    assert result['text'].strip() == "this is *test *email"
    assert result['subject'] == "Test email"
    assert result['from_address'] == "sergey@cheparev.com"
    assert result['full_name'] == "Sergey Cheparev"
    assert result['gmail_message_id'] == "1688b0102744bab7"
    assert result['gmail_thread_id'] == "1688b00c9ec9d5e7"


@pytest.fixture
def quoted_email_text():
    return """

    Hi Mark,


> this is inner quotation


and it should remain in the text

Best,
Sergey


> Hi Sergey,
>
> outer quotation should be removed
>
> Best,
> Mark
>
    """


def test_parse_message_remove_quotation(quoted_email_text):
    result = remove_quotation(quoted_email_text)
    assert "inner quotation" in result
    assert "outer quotation" not in result


@pytest.fixture
def parsed_message(gmail_api_message):
    return parse_message(gmail_api_message)


@pytest.mark.django_db
def test_associate_new(parsed_message):
    message = associate(parsed_message)
    assert message.sent_at == parsed_message['sent_at']
    assert message.subject == parsed_message['subject']
    assert message.project.name == parsed_message['subject']
    assert message.project.manager.company.name == "Cheparev"
    assert message.project.manager == message.author

    assert message.author.email == parsed_message['from_address']
    assert message.author.full_name == parsed_message['full_name']

    assert message.text == parsed_message['text']
    assert message.gmail_message_id == parsed_message['gmail_message_id']
    assert message.gmail_thread_id == parsed_message['gmail_thread_id']


@pytest.mark.django_db
def test_associate_manager_exists(employee,
                                  parsed_message):
    parsed_message['from_address'] = employee.email
    message = associate(parsed_message)
    assert message.author == employee


@pytest.mark.django_db
def test_associate_company_exists(company, parsed_message):
    parsed_message['from_address'] = f"test@{company.domain}"
    message = associate(parsed_message)
    assert message.project.manager.company == company


@pytest.mark.django_db
def test_associate_project_messages_exist(project, project_message_factory, parsed_message):
    existing_message = project_message_factory.create(project=project)
    parsed_message['subject'] = existing_message.subject
    parsed_message['gmail_thread_id'] = existing_message.gmail_thread_id
    parsed_message['from_email'] = f"another_manager@{existing_message.project.manager.company.domain}"
    message = associate(parsed_message)
    assert message.project == existing_message.project
    assert message.project.manager.company == existing_message.project.manager.company


@pytest.mark.django_db
def test_associate_project_exists_manager_match(project, parsed_message):
    parsed_message['from_address'] = project.manager.email
    message = associate(parsed_message)
    assert message.project == project


@pytest.mark.django_db
def test_associate_project_not_exist_manager_exists(employee, parsed_message):
    parsed_message['from_address'] = employee.email
    assert employee.projects.count() == 0
    message = associate(parsed_message)
    assert message.project.manager == employee
    assert message.project.name == parsed_message['subject']
    assert message.project.original_description == parsed_message['text']
    assert message.project.location == employee.company.location


@pytest.mark.django_db
def test_project_exists_inactive(project_factory, parsed_message):
    inactive_project = project_factory.create(state='stopped')
    parsed_message['from_address'] = inactive_project.manager.email
    message = associate(parsed_message)
    assert message.project != inactive_project
    assert message.project.manager == inactive_project.manager


@pytest.mark.django_db
def test_message_already_processed(project_message, parsed_message):
    parsed_message['gmail_message_id'] = project_message.gmail_message_id
    parsed_message['gmail_thread_id'] = project_message.gmail_thread_id
    message = associate(parsed_message)
    assert message == project_message


@pytest.fixture
def raw_email():
    message = EmailMessage()
    message.set_payload("xxx")
    message['message-id'] = str(uuid.uuid4())
    return message


@pytest.mark.django_db
def test_project_states(project):
    assert project.state == 'requested'
    project.scope()
    project.introduce()
    project.sign()
    project.start()
    project.finish()
    project.drop()


@pytest.fixture
def project_pages(project_page_factory):
    matching_page = project_page_factory.create(technologies=['xxx'])
    not_matching_page = project_page_factory.create()
    return [matching_page, not_matching_page]


@pytest.mark.django_db
def test_cv_set_relevant_projects(cv, project_pages, mocker):
    technology = Technology.objects.filter(name='xxx')
    mocker.patch('home.models.Technology.match_text',
                 side_effect=lambda *args: technology)

    cv.set_relevant_skills_and_projects()
    assert list(cv.relevant_project_pages.all()) == [project_pages[0]]
    assert list(cv.relevant_skills.all()) == [technology[0]]


@pytest.mark.django_db
def test_project_logo(project):
    assert project.company is not None
    assert project.company.logo is not None
    assert project.logo is project.company.logo

    project.company.logo = None
    assert project.logo is project.company.logo is None

    project.company = None
    assert project.logo is None


@pytest.mark.django_db
def test_auto_project_name(project_factory):
    project_without_company = project_factory.create()
    assert project_without_company.name == str(project_without_company.company)
    project_without_company = project_factory.create(company=None)
    assert project_without_company.name == str(project_without_company.company)


@pytest.mark.django_db
def test_invoice_copy_company_params(invoice):
    assert invoice.project.manager.company.payment_address
    assert invoice.project.manager.company.vat_id
    assert invoice.project.company.vat_id

    assert invoice.project
    invoice.payment_address = ""
    invoice.sender_vat_id = ""
    invoice.save()
    assert invoice.payment_address == invoice.project.manager.company.payment_address
    assert invoice.sender_vat_id == invoice.project.manager.company.vat_id

    invoice.payment_address = ""
    invoice.project.manager = None
    invoice.save()
    assert invoice.payment_address == invoice.project.company.payment_address
    assert invoice.sender_vat_id == invoice.project.company.vat_id

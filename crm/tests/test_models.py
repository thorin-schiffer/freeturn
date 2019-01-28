import json
import uuid
from datetime import date
from datetime import timedelta
from email.message import Message as EmailMessage

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from crm.gmail_utils import parse_message
from crm.models import ProjectMessage
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
    with open("data/gmail_api_message.json", "r") as f:
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
def parsed_message():
    return parse_message(gmail_api_message)


@pytest.mark.django_db
def test_associate_new(project, parsed_message):
    assert parsed_message not in project.messages.all()
    ProjectMessage.associate(parsed_message)
    assert parsed_message in project.messages.all()


def test_associate_manager_exists():
    raise NotImplementedError()


def test_associate_company_exists():
    raise NotImplementedError()


def test_associate_project_exists():
    raise NotImplementedError()


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
    assert project.company.logo is not None
    assert project.recruiter.logo is not None

    assert project.company is not None
    assert project.logo is project.company.logo

    project.company.logo = None
    assert project.logo is project.recruiter.logo

    project.company = None
    assert project.recruiter is not None
    assert project.logo is project.recruiter.logo


@pytest.mark.django_db
def test_auto_project_name(project_factory):
    project_without_company = project_factory.create()
    assert project_without_company.name == str(project_without_company.company)
    project_without_company = project_factory.create(company=None)
    assert project_without_company.name == str(project_without_company.recruiter)

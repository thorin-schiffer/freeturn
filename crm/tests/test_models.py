import uuid
from datetime import timedelta, date

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from crm.models import ProjectMessage
import django_mailbox.models
from email.message import Message as EmailMessage

from home.models import TechnologyInfo


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


@pytest.mark.django_db
def test_associate(project,
                   message,
                   monkeypatch):
    monkeypatch.setattr(message, 'from_header', f"Max Mustermann <{project.manager.email}>")
    assert message not in project.messages.all()
    ProjectMessage.associate(message)
    assert message in project.messages.all()


@pytest.fixture
def raw_email():
    message = EmailMessage()
    message.set_payload("xxx")
    message['message-id'] = str(uuid.uuid4())
    return message


@pytest.mark.django_db
def test_non_repeat_get_mail(mailbox,
                             monkeypatch,
                             mocker,
                             raw_email):
    connection = mocker.MagicMock()
    connection.get_message = lambda x: [raw_email]
    mocker.patch('django_mailbox.models.Mailbox.get_connection', side_effect=lambda: connection)
    result = mailbox.get_new_mail()[0]
    assert result.message_id == raw_email['message-id']

    assert django_mailbox.models.Message.objects.filter(message_id=raw_email['message-id']).count() == 1

    # call again, no new messages should be created
    mailbox.get_new_mail()
    assert django_mailbox.models.Message.objects.filter(message_id=raw_email['message-id']).count() == 1


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
    technology_info = TechnologyInfo.objects.filter(tag__name='xxx')
    mocker.patch('home.models.TechnologyInfo.match_text',
                 side_effect=lambda *args: technology_info)

    cv.set_relevant_skills_and_projects()
    assert list(cv.relevant_project_pages.all()) == [project_pages[0]]
    assert list(cv.relevant_skills.all()) == [technology_info[0].tag]

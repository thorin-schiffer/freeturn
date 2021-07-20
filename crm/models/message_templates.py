from django.db.models import CharField
from django_extensions.db.models import TimeStampedModel
from wagtail.core.fields import RichTextField

from crm.models import Project


def get_project_state_transitions():
    transitions = list(Project._meta.get_field('state').get_all_transitions(Project))
    return [(transition.name, transition.name.capitalize()) for transition in transitions]


class MessageTemplate(TimeStampedModel):
    text = RichTextField(help_text='Text of the message')
    state_transition = CharField(max_length=50,
                                 choices=get_project_state_transitions(),
                                 help_text='Project state transition this message template '
                                           'will be associated with, if any',
                                 unique=True, null=True, blank=True, default=None)
    name = CharField(max_length=100)

    def __str__(self):
        return self.name

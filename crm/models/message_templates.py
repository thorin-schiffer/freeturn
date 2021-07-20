from django.core.exceptions import ValidationError
from django.db.models import CharField
from django.template import Template, Context, TemplateSyntaxError
from django_extensions.db.models import TimeStampedModel
from wagtail.core.fields import RichTextField
from django.conf import settings
from crm.models import Project


def get_project_state_transitions():
    transitions = list(Project._meta.get_field('state').get_all_transitions(Project))
    return [(transition.name, transition.name.capitalize()) for transition in transitions]


def valid_django_template(value):
    try:
        template = Template(value)
        template.render(Context({}))
        return value
    except TemplateSyntaxError as ex:
        raise ValidationError(f'Invalid template: {ex}')


class MessageTemplate(TimeStampedModel):
    text = RichTextField(help_text='Text of the message',
                         validators=[valid_django_template])
    state_transition = CharField(max_length=50,
                                 choices=get_project_state_transitions(),
                                 help_text='Project state transition this message template '
                                           'will be associated with, if any',
                                 null=True, blank=True, default=None)
    name = CharField(max_length=100)
    language = CharField(choices=settings.LANGUAGES, max_length=10, default='en')

    def __str__(self):
        return self.name

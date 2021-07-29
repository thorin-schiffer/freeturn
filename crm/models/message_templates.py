from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import CharField, BooleanField
from django.template import Template, Context, TemplateSyntaxError
from django_extensions.db.models import TimeStampedModel
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.core.fields import RichTextField

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
    text = RichTextField(help_text='Text of the message. '
                                   'Following context is available:'
                                   '{{project}} - project'
                                   '{{project.manager}} - manager'
                                   '{{project.company}} - company',
                         validators=[valid_django_template])
    state_transition = CharField(max_length=50,
                                 choices=get_project_state_transitions(),
                                 help_text='Project state transition this message template '
                                           'will be associated with, if any',
                                 null=True, blank=True, default=None)
    name = CharField(max_length=100)
    language = CharField(choices=settings.LANGUAGES, max_length=10, default='en')
    attach_cv = BooleanField(default=True,
                             help_text='Attach CV by default for this template',
                             verbose_name='Attach CV')
    panels = [
        MultiFieldPanel([
            FieldPanel('name'),
            FieldPanel('text'),
        ]),
        MultiFieldPanel([
            FieldPanel('state_transition'),
            FieldPanel('language'),
            FieldPanel('attach_cv')
        ], heading='Options')
    ]

    def __str__(self):
        return self.name

from django.db import models
from django_fsm import FSMField, transition


class ProjectStateMixin(models.Model):
    state = FSMField(default='requested', editable=False)

    @transition(field=state, source='requested', target='scoped', custom={
        "help": "This project was scoped, on email or call",
        "fields": ["location", "daily_rate", "notes"]
    })
    def scope(self):
        pass

    @transition(field=state, source='scoped', target='introduced', custom={
        "help": "Introduced to the end client",
        "fields": ["company", "notes"]
    })
    def introduce(self):
        pass

    @transition(field=state, source='introduced', target='signed', custom={
        "help": "Contract signed",
        "fields": ["company", "notes"]
    })
    def sign(self):
        pass

    @transition(field=state, source='signed', target='progress', custom={
        "help": "Started working",
        "fields": ["notes"]
    })
    def start(self):
        pass

    @transition(field=state, source='progress', target='finished', custom={
        "help": "Finished working",
        "fields": ["notes"]
    })
    def finish(self):
        pass

    @transition(field=state, source='*', target='stopped', custom={
        "help": "Project dropped",
        "classes": ["no"],
        "fields": ["notes"]
    })
    def drop(self):
        pass

    class Meta:
        abstract = True

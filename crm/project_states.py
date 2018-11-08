from django.db import models
from django_fsm import FSMField, transition


class ProjectStateMixin(models.Model):
    state = FSMField(default='requested', protected=True, editable=False)

    @transition(field=state, source='requested', target='scoped')
    def scope(self):
        pass

    @transition(field=state, source='scoped', target='introduced')
    def introduce(self):
        pass

    @transition(field=state, source='inroduced', target='signed')
    def sign(self):
        pass

    @transition(field=state, source='signed', target='progress')
    def start(self):
        pass

    @transition(field=state, source='progress', target='finished')
    def finish(self):
        pass

    @transition(field=state, source='*', target='stopped')
    def stop(self):
        pass

    class Meta:
        abstract = True

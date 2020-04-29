from django.db import models
from django.utils import timezone
from django_extensions.db.models import TimeStampedModel


class ProjectMessage(TimeStampedModel):
    project = models.ForeignKey('Project',
                                null=True,
                                blank=True,
                                on_delete=models.SET_NULL,
                                related_name='messages')
    author = models.ForeignKey('Employee',
                               on_delete=models.CASCADE,
                               related_name='messages')
    sent_at = models.DateTimeField(default=timezone.now,
                                   help_text='Sending time')
    subject = models.CharField(max_length=200,
                               blank=True,
                               null=True)
    text = models.TextField()

    gmail_message_id = models.CharField(max_length=50)
    gmail_thread_id = models.CharField(max_length=50)

    def __str__(self):
        return str(self.subject)

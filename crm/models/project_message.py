from django.db import models
from django.utils import timezone
from django_extensions.db.models import TimeStampedModel
from instance_selector.edit_handlers import InstanceSelectorPanel
from wagtail.admin.edit_handlers import FieldPanel, FieldRowPanel, MultiFieldPanel


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
    message_id = models.CharField(max_length=300, help_text='Message-id header of the original message')
    reply_to = models.EmailField(help_text='Reply-to header of the original message')

    panels = [
        FieldRowPanel([
            MultiFieldPanel([
                InstanceSelectorPanel('project'),
                FieldPanel('subject'),
                FieldPanel('text'),
            ]),
        ]),
        FieldRowPanel([
            MultiFieldPanel([
                InstanceSelectorPanel('author'),
                FieldPanel('sent_at'),
            ]),
            MultiFieldPanel([
                FieldPanel('gmail_message_id'),
                FieldPanel('gmail_thread_id'),
                FieldPanel('message_id'),
                FieldPanel('reply_to'),
            ])
        ])
    ]

    def __str__(self):
        return str(self.subject)

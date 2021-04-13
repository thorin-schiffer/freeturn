from django.db import models
from fuzzywuzzy import process
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.fields import RichTextField
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.models import register_snippet


@register_snippet
class Technology(index.Indexed, models.Model):
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    summary = RichTextField(blank=True)
    name = models.CharField(max_length=100, unique=True)
    match_in_cv = models.BooleanField(default=True,
                                      help_text='Match for technology in CV relevant projects?')
    panels = [
        FieldPanel('name'),
        ImageChooserPanel('logo'),
        FieldPanel('summary'),
    ]
    search_fields = [
        index.SearchField('name', partial_match=True),
    ]

    @staticmethod
    def match_text(text, limit=5, cutoff=40):
        choices = Technology.objects.filter(match_in_cv=True).values_list(
            'name', flat=True
        )
        if not choices.exists():
            return Technology.objects.none()
        results = process.extract(text, choices, limit=limit)
        return Technology.objects.filter(
            name__in=[r[0] for r in results if r[1] > cutoff]
        )

    autocomplete_search_field = 'name'

    def autocomplete_label(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'technology'
        verbose_name_plural = 'technologies'


@register_snippet
class Responsibility(models.Model):
    text = models.CharField(max_length=200)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name_plural = 'responsibilities'

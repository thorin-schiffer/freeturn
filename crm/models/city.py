from django.db import models
from django.db.models import Count


class City(models.Model):
    name = models.CharField(max_length=200,
                            unique=True)

    @property
    def project_count(self):
        return self.projects.count()

    @classmethod
    def most_popular(cls):
        return cls.objects.annotate(c=Count('projects')).order_by('-c').first()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'city'

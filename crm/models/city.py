from django.db import models


class City(models.Model):
    name = models.CharField(max_length=200,
                            unique=True)

    @property
    def project_count(self):
        return self.projects.count()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'city'

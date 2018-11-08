# Generated by Django 2.0.9 on 2018-11-08 14:02

from django.db import migrations, models
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0009_project_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientcompany',
            name='url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='recruiter',
            name='url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='state',
            field=django_fsm.FSMField(default='requested', editable=False, max_length=50),
        ),
    ]

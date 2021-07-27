# Generated by Django 3.2.5 on 2021-07-20 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0018_messagetemplate_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messagetemplate',
            name='state_transition',
            field=models.CharField(blank=True, choices=[('drop', 'Drop'), ('finish', 'Finish'), ('introduce', 'Introduce'), ('scope', 'Scope'), ('sign', 'Sign'), ('start', 'Start')], default=None, help_text='Project state transition this message template will be associated with, if any', max_length=50, null=True),
        ),
    ]

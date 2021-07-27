# Generated by Django 3.2.5 on 2021-07-20 12:21

from django.db import migrations, models
import django_extensions.db.fields
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0016_alter_cv_project_listing_title'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('text', wagtail.core.fields.RichTextField(help_text='Text of the message')),
                ('state_transition', models.CharField(blank=True, choices=[('drop', 'DROP'), ('finish', 'FINISH'), ('introduce', 'INTRODUCE'), ('scope', 'SCOPE'), ('sign', 'SIGN'), ('start', 'START')], default=None, help_text='Project state transition this message template will be associated with, if any', max_length=50, null=True, unique=True)),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
    ]

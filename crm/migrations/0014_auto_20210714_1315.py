# Generated by Django 3.2.4 on 2021-07-14 13:15

from django.db import migrations
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0013_auto_20210630_1300'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cv',
            name='working_permit',
            field=wagtail.core.fields.RichTextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='cvgenerationsettings',
            name='default_working_permit',
            field=wagtail.core.fields.RichTextField(blank=True, default='PERMANENT RESIDENCE', null=True),
        ),
    ]

# Generated by Django 3.2.4 on 2021-07-14 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0008_auto_20210630_1300'),
    ]

    operations = [
        migrations.AddField(
            model_name='homepage',
            name='services',
            field=models.CharField(default='Python, Django, Wagtail', help_text='Services you want to highlight', max_length=500),
        ),
    ]
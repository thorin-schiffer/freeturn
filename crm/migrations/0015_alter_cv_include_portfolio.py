# Generated by Django 3.2.5 on 2021-07-20 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0014_auto_20210714_1315'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cv',
            name='include_portfolio',
            field=models.BooleanField(default=False, help_text="Include portfolio projects' description"),
        ),
    ]
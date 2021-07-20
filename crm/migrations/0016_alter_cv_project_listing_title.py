# Generated by Django 3.2.5 on 2021-07-20 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0015_alter_cv_include_portfolio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cv',
            name='project_listing_title',
            field=models.CharField(default='Relevant projects', help_text="The title of your project listing, something like 'my projects' or 'recent projects'", max_length=200),
        ),
    ]
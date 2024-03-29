# Generated by Django 3.2.5 on 2021-08-04 13:45

from django.db import migrations
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0028_alter_messagetemplate_language'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cvgenerationsettings',
            name='default_contact_details',
            field=wagtail.core.fields.RichTextField(blank=True, default='thorin@schiffer.pro', null=True),
        ),
        migrations.AlterField(
            model_name='cvgenerationsettings',
            name='default_education_overview',
            field=wagtail.core.fields.RichTextField(blank=True, default='Novosibirsk State Technical University', help_text='Notice on your education', null=True),
        ),
        migrations.AlterField(
            model_name='cvgenerationsettings',
            name='default_experience_overview',
            field=wagtail.core.fields.RichTextField(blank=True, default='Python developer experience: 7 years', help_text='Notice on your experience', null=True),
        ),
        migrations.AlterField(
            model_name='cvgenerationsettings',
            name='default_languages_overview',
            field=wagtail.core.fields.RichTextField(blank=True, default='English: fluent', null=True),
        ),
        migrations.AlterField(
            model_name='cvgenerationsettings',
            name='default_rate_overview',
            field=wagtail.core.fields.RichTextField(blank=True, default='100 schmeckles', null=True),
        ),
    ]

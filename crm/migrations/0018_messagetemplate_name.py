# Generated by Django 3.2.5 on 2021-07-20 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0017_messagetemplate'),
    ]

    operations = [
        migrations.AddField(
            model_name='messagetemplate',
            name='name',
            field=models.CharField(default='name', max_length=100),
            preserve_default=False,
        ),
    ]
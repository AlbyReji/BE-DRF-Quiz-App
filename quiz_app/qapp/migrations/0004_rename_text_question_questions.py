# Generated by Django 4.2.3 on 2023-07-19 03:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('qapp', '0003_question'),
    ]

    operations = [
        migrations.RenameField(
            model_name='question',
            old_name='text',
            new_name='questions',
        ),
    ]

# Generated by Django 4.2.3 on 2023-07-19 17:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('qapp', '0007_quizsubmission'),
    ]

    operations = [
        migrations.RenameField(
            model_name='choice',
            old_name='question',
            new_name='qtn',
        ),
        migrations.RenameField(
            model_name='question',
            old_name='question',
            new_name='qtn',
        ),
    ]

# Generated by Django 4.2.3 on 2023-07-19 03:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('qapp', '0004_rename_text_question_questions'),
    ]

    operations = [
        migrations.RenameField(
            model_name='question',
            old_name='questions',
            new_name='question',
        ),
    ]

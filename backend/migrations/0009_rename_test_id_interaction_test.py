# Generated by Django 4.1 on 2022-08-06 19:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0008_candidate_interaction_response'),
    ]

    operations = [
        migrations.RenameField(
            model_name='interaction',
            old_name='test_id',
            new_name='test',
        ),
    ]

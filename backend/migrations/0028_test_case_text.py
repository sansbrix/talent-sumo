# Generated by Django 4.1 on 2022-11-16 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0027_test_assesment_test_library'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='case_text',
            field=models.TextField(default=None, null=True),
        ),
    ]

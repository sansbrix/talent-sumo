# Generated by Django 4.1 on 2022-08-29 19:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "backend",
            "0017_rename_audio_aggregate_content_scoe_audioscore_audio_aggregate_content_score",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="scoreperquestion",
            name="score",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="backend.score",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="textscoreperquestion",
            name="score",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="backend.score",
            ),
            preserve_default=False,
        ),
    ]

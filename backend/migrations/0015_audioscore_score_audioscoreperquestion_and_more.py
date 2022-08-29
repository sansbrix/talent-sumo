# Generated by Django 4.0.2 on 2022-08-24 16:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0014_userdetail"),
    ]

    operations = [
        migrations.CreateModel(
            name="AudioScore",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("audio_sales_quotient", models.CharField(max_length=400)),
                ("audio_manager_quotient", models.CharField(max_length=400)),
                ("audio_leadership_quotient", models.CharField(max_length=400)),
                ("audio_learner_quotient", models.CharField(max_length=400)),
                ("audio_sales_quotient_percentile", models.CharField(max_length=400)),
                ("audio_people_qutient_percentile", models.CharField(max_length=400)),
                ("audio_pace", models.CharField(max_length=600)),
                ("audio_pitch", models.CharField(max_length=600)),
                ("audio_power_word_density", models.CharField(max_length=600)),
                ("audio_word_cloud", models.CharField(max_length=600)),
                ("audio_volume", models.CharField(max_length=600)),
                ("audio_aggregate_content_scoe", models.CharField(max_length=400)),
                ("audio_raw_interaction_score", models.CharField(max_length=400)),
                ("audio_interaction_score", models.CharField(max_length=400)),
                ("audio_energy", models.CharField(max_length=400)),
            ],
        ),
        migrations.CreateModel(
            name="Score",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("mcq_percentage", models.CharField(max_length=400)),
                ("manager_quotient_percentile", models.CharField(max_length=400)),
                ("leadership_quotient_percentile", models.CharField(max_length=400)),
                ("learner_quotient_percentile", models.CharField(max_length=400)),
                ("people_quotient", models.CharField(max_length=400)),
                ("resume_score", models.CharField(max_length=500)),
                ("video_estimated_gesture_score", models.CharField(max_length=400)),
                ("interaction_percentile", models.CharField(max_length=400)),
                (
                    "interaction",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="backend.interaction",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="AudioScorePerQuestion",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("audio_transcript", models.CharField(max_length=500)),
                ("audio_confidence", models.CharField(max_length=500)),
                ("audio_fluency", models.CharField(max_length=500)),
                ("grammer_score", models.CharField(max_length=500)),
                ("audio_content_score", models.CharField(max_length=400)),
                ("audio_per_question_content_score", models.CharField(max_length=400)),
                ("audio_silence_number", models.CharField(max_length=400)),
                ("audio_silence_length", models.CharField(max_length=400)),
                ("audio_filler_words_score", models.CharField(max_length=400)),
                ("audio_sentiment_score", models.CharField(max_length=400)),
                (
                    "audio_score",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="backend.audioscore",
                    ),
                ),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="backend.question",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="audioscore",
            name="score",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="backend.score"
            ),
        ),
    ]

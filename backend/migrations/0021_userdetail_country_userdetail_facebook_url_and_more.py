# Generated by Django 4.1 on 2022-09-11 04:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0020_score_charm_aggregate_score_confidence_aggregate_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="userdetail",
            name="country",
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="userdetail",
            name="facebook_url",
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="userdetail",
            name="instagram_url",
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="userdetail",
            name="institute_name",
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="userdetail",
            name="linkedin_url",
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="userdetail",
            name="phone_number",
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="userdetail",
            name="twitter_url",
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
    ]

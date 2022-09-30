from operator import mod
from tkinter import CASCADE

from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import post_save
# Create your models here.
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags
from django_rest_passwordreset.signals import reset_password_token_created

from talentsumo import env


# Test Model
class Test(models.Model):
    is_creator_comapany = models.IntegerField(null=True, blank=True)
    institute_name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    test_code = models.CharField(max_length=255)
    track = models.CharField(max_length=255)
    interaction_mode = models.CharField(max_length=255)  # Interview Mode
    report_type = models.CharField(max_length=255)
    report_type_text = models.CharField(max_length=255, null=True, blank=True)
    generate_certificate = models.CharField(max_length=255)
    generate_certificate_text = models.CharField(max_length=255, null=True, blank=True)
    job_instruction = models.CharField(max_length=255)
    job_describtion = models.CharField(max_length=255)
    access_code = models.CharField(max_length=255)
    expiry_date = models.DateField()
    who_can_initiate = models.CharField(max_length=255)
    timer = models.CharField(max_length=255)
    collect_mail = models.BooleanField()
    collect_resume = models.BooleanField()
    collect_candidate_feedback_message = models.BooleanField()
    collect_channel = models.CharField(max_length=255)
    collect_candidate_id = models.BooleanField()
    collect_voice_match = models.BooleanField()
    total_question = models.IntegerField()
    mentor_name = models.CharField(max_length=255, default=None, null=True, blank=True)
    insights = models.CharField(max_length=255, default=None, blank=True, null=True)
    external_bot = models.BooleanField(default=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    createdby = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="test_craeted_by"
    )
    updated_at = models.DateTimeField(auto_now=True)
    updatedby = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="test_updated_by"
    )
    is_active = models.BooleanField(default=True)


# Notification Model
class Notification(models.Model):
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notification",
    )
    interaction_welcome_message = models.CharField(max_length=255)
    interaction_instruction_message = models.CharField(max_length=255)
    interaction_completion_message = models.CharField(max_length=255)
    bot_warning_message = models.CharField(max_length=255)
    report_send_to_user = models.BooleanField()
    report_sent_to_email_one = models.CharField(max_length=255, null=True, blank=True)
    report_sent_to_email_two = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    createdby = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notification_created_by"
    )
    updated_at = models.DateTimeField(auto_now=True)
    updatedby = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notification_updated_by"
    )


# Question Model
class Question(models.Model):
    question = models.CharField(max_length=255)
    answer_format = models.CharField(max_length=255)
    ideal_answer = models.CharField(max_length=255)
    test = models.ForeignKey(
        Test, on_delete=models.CASCADE, null=True, blank=True, related_name="questions"
    )
    rated = models.BooleanField()
    content_rated = models.BooleanField(null=True, blank=True)
    should_score = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    createdby = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="question_craeted_by"
    )
    media_link = models.CharField(max_length=255, null=True, default=None, blank=True)
    question_context = models.CharField(
        max_length=255, null=True, default=None, blank=True
    )
    updated_at = models.DateTimeField(auto_now=True)
    updatedby = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="question_updated_by"
    )
    is_active = models.BooleanField(default=True)
    mcq_option_one = models.CharField(
        max_length=255, default=None, blank=True, null=True
    )
    mcq_option_two = models.CharField(
        max_length=255, default=None, blank=True, null=True
    )
    mcq_option_three = models.CharField(
        max_length=255, default=None, blank=True, null=True
    )
    mcq_option_four = models.CharField(
        max_length=255, default=None, blank=True, null=True
    )


class Candidate(models.Model):
    name = models.CharField(max_length=255, default=None, null=False, blank=False)
    access_code = models.CharField(
        max_length=255, default=True, null=False, blank=False
    )
    phone_number = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # createdby_id
    # updatedby_id


class Interaction(models.Model):
    start_rating = models.CharField(max_length=255, null=True, blank=True, default=None)
    rating_description = models.CharField(
        max_length=255, null=True, blank=True, default=None
    )
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    candidate_feedback = models.CharField(
        max_length=255, null=True, blank=True, default=None
    )
    report_send_to_user = models.BooleanField()
    channel_1 = models.CharField(max_length=255, null=True, blank=True)
    channel_2 = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    # score_id =
    # individual_report_id=
    

STATUS_CHOICES = (
    ("response-received", "response-received"),
    ("in-progress", "in-progress"),
    ("done", "done"),
)
class Response(models.Model):
    response = models.CharField(max_length=255)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    interaction = models.ForeignKey(Interaction, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    status = models.CharField(
        choices=(STATUS_CHOICES), default="response-received", max_length=255
    )
    # createdby_id
    # updatedby_id


class UserDetail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    invitation_code = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="This code tell us which user is invite this user.",
    )
    invitation_code_optional = models.BooleanField(default=False)
    invite_code = models.CharField(
        max_length=255,
        help_text="This is the code with that user can invite the other user.",
    )
    phone_number = models.CharField(max_length=255, null=True, default=True, blank=True)
    institute_name = models.CharField(
        max_length=255, null=True, default=True, blank=True
    )
    country = models.CharField(max_length=255, null=True, default=True, blank=True)
    linkedin_url = models.CharField(max_length=255, null=True, default=True, blank=True)
    facebook_url = models.CharField(max_length=255, null=True, default=True, blank=True)
    twitter_url = models.CharField(max_length=255, null=True, default=True, blank=True)
    instagram_url = models.CharField(
        max_length=255, null=True, default=True, blank=True
    )
    business_invite_code = models.CharField(max_length=255, null=True, default=None, blank=True, help_text="This is the code with that user signed up in the signup page.",)
    number_of_interaction = models.CharField(max_length=255, null=True, default=None, blank=True)
    number_of_responses = models.CharField(max_length=255, null=True, default=None, blank=True)
    video_creator = models.BooleanField(null=True, default=None, blank=True)
    external_bot_user = models.BooleanField(null=True, default=None, blank=True)
    user_type = models.CharField(max_length=255, null=True, blank=True, default=None)
    


@receiver(reset_password_token_created)
def password_reset_token_created(
    sender, instance, reset_password_token, *args, **kwargs
):
    email_plaintext_message = (
        "Please provide the token to reset the password {}".format(
            reset_password_token.key
        )
    )
    send_mail(
        # title:
        "Password Reset for {title}".format(title="TalentSumo"),
        # message:
        email_plaintext_message,
        # from:
        "noreply@talentsumo.com",
        # to:
        [reset_password_token.user.email],
    )


class Score(models.Model):
    interaction = models.ForeignKey(Interaction, on_delete=models.CASCADE)
    mcq_percentage = models.CharField(max_length=400)
    manager_quotient_percentile = models.CharField(max_length=400)
    leadership_quotient_percentile = models.CharField(max_length=400)
    learner_quotient_percentile = models.CharField(max_length=400)
    people_quotient = models.CharField(max_length=400)
    resume_score = models.CharField(max_length=500)
    video_estimated_gesture_score = models.CharField(max_length=400)
    interaction_percentile = models.CharField(max_length=400)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    likeability_aggregate = models.CharField(
        max_length=255, null=True, blank=True, default=None
    )
    charm_aggregate = models.CharField(
        max_length=255, null=True, blank=True, default=None
    )
    fluency_agreegate = models.CharField(
        max_length=255, null=True, blank=True, default=None
    )
    confidence_aggregate = models.CharField(
        max_length=255, null=True, blank=True, default=None
    )
    energy_aggregate = models.CharField(
        max_length=255, null=True, blank=True, default=None
    )


class AudioScore(models.Model):
    score = models.ForeignKey(Score, on_delete=models.CASCADE)
    audio_sales_quotient = models.CharField(max_length=400)
    audio_manager_quotient = models.CharField(max_length=400)
    audio_leadership_quotient = models.CharField(max_length=400)
    audio_learner_quotient = models.CharField(max_length=400)
    audio_sales_quotient_percentile = models.CharField(max_length=400)
    audio_people_qutient_percentile = models.CharField(max_length=400)
    audio_pace = models.CharField(max_length=600)
    audio_pitch = models.CharField(max_length=600)
    audio_power_word_density = models.CharField(max_length=600)
    audio_word_cloud = models.CharField(max_length=600)
    audio_volume = models.CharField(max_length=600)
    audio_aggregate_content_score = models.CharField(max_length=400)
    audio_raw_interaction_score = models.CharField(max_length=400)
    audio_interaction_score = models.CharField(max_length=400)
    audio_energy = models.CharField(max_length=400)


class AudioScorePerQuestion(models.Model):
    audio_score = models.ForeignKey(AudioScore, on_delete=models.CASCADE)
    audio_transcript = models.CharField(max_length=500)
    audio_confidence = models.CharField(max_length=500)
    audio_fluency = models.CharField(max_length=500)
    grammer_score = models.CharField(max_length=500)
    audio_content_score = models.CharField(max_length=400)
    audio_per_question_content_score = models.CharField(max_length=400)
    audio_silence_number = models.CharField(max_length=400)
    audio_silence_length = models.CharField(max_length=400)
    audio_filler_words_score = models.CharField(max_length=400)
    audio_sentiment_score = models.CharField(max_length=400)


class ScorePerQuestion(models.Model):
    score = models.ForeignKey(Score, on_delete=models.CASCADE)
    mcq_value = models.CharField(max_length=400)
    video_likeability = models.CharField(max_length=400)
    video_charm = models.CharField(max_length=400)


class TextScorePerQuestion(models.Model):
    score = models.ForeignKey(Score, on_delete=models.CASCADE)
    question_grammer_score = models.CharField(max_length=400)


# @receiver(post_save, sender=Score, dispatch_uid="send_intrection_email")
# def email_notification_for_mcq_tests(sender, instance, *args, **kwargs):
#     subject = "Thank you for attempting the test | TalentSumo"
#     html_message = render_to_string(
#         "email_notification_for_mcq.html", {"instance": instance}
#     )
#     plain_message = strip_tags(html_message)
#     from_email = "From <from@example.com>"
#     to = "to@example.com"
#     send_mail(subject, plain_message, from_email, [to], html_message=html_message)

class BusinessInvitationCode(models.Model):
    invitation_code = models.CharField(max_length=255)
    number_of_interaction = models.CharField(max_length=255)
    number_of_responses_per_test = models.CharField(max_length=255)
    employee = models.BooleanField()
    expiry_date = models.CharField(max_length=255, null=True, blank=True)
    external_bot_user = models.BooleanField()
    video_creator = models.BooleanField()
    team_user = models.BooleanField()
    one_time_user = models.BooleanField()
    user_type = models.CharField(max_length=255)
    
    
from pyexpat import model
from django.db import models

# Create your models here.
from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail  
from talentsumo import env
from django.contrib.auth.models import User

# Test Model
class Test(models.Model):
    is_creator_comapany = models.IntegerField(null=True, blank=True)
    institute_name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    test_code = models.CharField(max_length=255)
    track = models.CharField(max_length=255)
    interaction_mode = models.CharField(max_length=255) # Interview Mode
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
    created_at = models.DateTimeField(auto_now_add=True)
    createdby = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_craeted_by')
    updated_at = models.DateTimeField(auto_now=True)
    updatedby = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_updated_by')
    is_active =  models.BooleanField(default=True)
    
 
# Notification Model
class Notification(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, null=True, blank=True, related_name='notification')
    interaction_welcome_message = models.CharField(max_length=255)
    interaction_instruction_message = models.CharField(max_length=255)
    interaction_completion_message = models.CharField(max_length=255)
    bot_warning_message = models.CharField(max_length=255)
    report_send_to_user = models.BooleanField()
    report_sent_to_email_one = models.CharField(max_length=255, null=True, blank=True) 
    report_sent_to_email_two = models.CharField(max_length=255, null=True, blank=True) 
    is_active =  models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    createdby = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_created_by')
    updated_at = models.DateTimeField(auto_now=True)
    updatedby = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_updated_by')
    
     
# Question Model
class Question(models.Model):
    question = models.CharField(max_length=255)
    answer_format = models.CharField(max_length=255)
    ideal_answer = models.CharField(max_length=255)
    test = models.ForeignKey(Test, on_delete=models.CASCADE, null=True, blank=True, related_name='questions')
    rated = models.BooleanField()
    content_rated = models.BooleanField(null=True, blank=True)
    should_score = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    createdby = models.ForeignKey(User, on_delete=models.CASCADE, related_name='question_craeted_by')
    updated_at = models.DateTimeField(auto_now=True)
    updatedby = models.ForeignKey(User, on_delete=models.CASCADE, related_name='question_updated_by')
    is_active =  models.BooleanField(default=True)
    mcq_option_one = models.CharField(max_length=255, default=None, blank=True, null=True)
    mcq_option_two = models.CharField(max_length=255, default=None, blank=True, null=True)
    mcq_option_three = models.CharField(max_length=255, default=None, blank=True, null=True)
    mcq_option_four = models.CharField(max_length=255, default=None, blank=True, null=True)
    

class Candidate(models.Model):
    name = models.CharField(max_length=255, default=None, null=False, blank=False)
    access_code = models.CharField(max_length=255, default=True, null=False, blank=False)
    phone_number = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # createdby_id
    # updatedby_id
    
class Interaction(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    candidate_feedback = models.CharField(max_length=255, null=True, blank=True, default=None)
    report_send_to_user = models.BooleanField()
    channel_1 = models.CharField(max_length=255, null=True, blank=True)
    channel_2 = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    # score_id = 
    # individual_report_id=
    
class Response(models.Model):
    response = models.CharField(max_length=255)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    interaction = models.ForeignKey(Interaction, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
     # createdby_id
    # updatedby_id
    
@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    email_plaintext_message = "Please provide the token to reset the password {}".format(reset_password_token.key)
    send_mail(
        # title:
        "Password Reset for {title}".format(title="TalentSumo"),
        # message:
        email_plaintext_message,
        # from:
        "noreply@talentsumo.com",
        # to:
        [reset_password_token.user.email]
    )
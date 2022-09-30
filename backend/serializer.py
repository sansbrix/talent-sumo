from ctypes import Array
from dataclasses import fields
from operator import mod
from os import access

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db import models
from pyexpat import model
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.validators import UniqueValidator

from backend.models import (AudioScore, AudioScorePerQuestion, Candidate,
                            Interaction, Notification, Question, Response,
                            Score, ScorePerQuestion, Test,
                            TextScorePerQuestion, UserDetail)

from .utils import create_user_invite_code


class IntrectionRatingSerializer(serializers.Serializer):
    start_rating = serializers.CharField()
    rating_description = serializers.CharField()


# Register serializer
class RegisterSerializer(serializers.ModelSerializer):
    invitation_code = serializers.CharField(required=False, write_only=True)
    business_invite_code = serializers.CharField(required=True, write_only=True)
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "password",
            "first_name",
            "last_name",
            "email",
            "invitation_code",
        )
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data["username"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            email=validated_data["email"],
        )
        code = (
            validated_data["invitation_code"]
            if validated_data.get("invitation_code")
            else None
        )
        UserDetail.objects.create(
            user=user,
            invite_code=create_user_invite_code(),
            invitation_code=code,
            invitation_code_optional=True if code else False,
        )
        return user


# User serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


# Change Password Serializer
class ChangePasswordSerializer(serializers.Serializer):
    model = User
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = "__all__"


class QuestionResponseSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(read_only=True)

    class Meta:
        model = Response
        fields = "__all__"


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"


# Test Serializer
class TestSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)
    notification = NotificationSerializer(many=True)

    class Meta:
        model = Test
        fields = "__all__"

        extra_kwargs = {
            "questions": {"write_only": True},
            "notification": {"write_only": True},
        }

    def create(self, validated_data):
        questions = validated_data.pop("questions")
        notification = validated_data.pop("notification")
        test = Test.objects.create(**validated_data)

        for i in questions:
            Question.objects.create(**i, test=test)

        for i in notification:
            Notification.objects.create(**i, test=test)
            break

        return test

    def update_test_object(self, instance, validated_data):
        Test.objects.filter(id=instance.id).update(**validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        questions = validated_data.pop("questions")
        notification = validated_data.pop("notification")

        self.update_test_object(instance, validated_data)

        questions_updated_ids = []
        for i in questions:
            if i.get("id") is None:
                Question.objects.create(**i)
            else:
                Question.objects.filter(id=i.get("id")).update(**i)
                questions_updated_ids.append(i.get("id"))

        # Delete the questions that are not coming
        questions_not_coming = Question.objects.filter(test=instance).values_list(
            "id", flat=True
        )
        intersection = set(questions_not_coming).difference(questions_updated_ids)
        Question.objects.filter(id__in=intersection).delete()

        notification_ = Notification.objects.filter(test=instance).first()
        for i in notification:
            if notification_ is None:
                i.pop("test")
                i["test"] = instance
                i["createdby"] = user
                i["updatedby"] = user
                Notification.objects.create(**i)
            else:
                Notification.objects.filter(id=i.get("id")).update(**i)

            break

        return instance


class FetchTestSerializer(serializers.Serializer):
    search = serializers.CharField(required=False)


class ValidateAccessCodeSerializer(serializers.Serializer):
    model = Test
    access_code = serializers.CharField(required=True)


class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Response
        fields = "__all__"

        extra_kwargs = {
            "candidate": {"read_only": True},
            "interaction": {"read_only": True},
        }


class CandidateSerializer(serializers.ModelSerializer):
    responses = ResponseSerializer(many=True, write_only=True)

    class Meta:
        model = Candidate
        fields = "__all__"
        extra_kwargs = {
            "responses": {"write_only": True},
        }

    def create(self, validated_data):
        responses = validated_data.pop("responses")
        candidate = Candidate.objects.create(**validated_data)
        test = Test.objects.filter(access_code=validated_data["access_code"]).last()
        notification = Notification.objects.get(test=test)
        interaction = Interaction.objects.create(
            candidate=candidate,
            test=test,
            candidate_feedback="",
            report_send_to_user=notification.report_send_to_user,
            channel_1=notification.report_sent_to_email_one,
            channel_2=notification.report_sent_to_email_two,
        )
        for i in responses:
            Response.objects.create(**i, interaction=interaction, candidate=candidate)

        return candidate


class InteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interaction
        fields = "__all__"
        extra_kwargs = {
            "candidate": {"read_only": True},
            "interaction": {"read_only": True},
        }


class OutputCSVToAISerializer(serializers.Serializer):
    file = serializers.FileField()


class ReportSerializer(serializers.ModelSerializer):
    job_title = serializers.ReadOnlyField(source="interaction.test.job_title")
    intrection_created_at = serializers.ReadOnlyField(source="interaction.created_at")
    candidate_name = serializers.ReadOnlyField(source="interaction.candidate.name")
    intreaction_score = serializers.ReadOnlyField(source="interaction.candidate.name")
    likeabilty = serializers.SerializerMethodField()  # video_likeability
    charm = serializers.SerializerMethodField()  # video_charm
    energy = serializers.SerializerMethodField()  # audio_energy
    fluency = serializers.SerializerMethodField()  # audio_fluency
    confidence = serializers.SerializerMethodField()  # audio_confidence
    estimated_gesture_score = (
        serializers.SerializerMethodField()
    )  # video_estimated_gesture_score
    sentiment_score = serializers.SerializerMethodField()  # audio_sentiment_score
    grammer_score = serializers.SerializerMethodField()  # question_grammer_score
    volume = serializers.SerializerMethodField()  # audio_volume
    pitch = serializers.SerializerMethodField()  # audio_pitch
    content_score = serializers.SerializerMethodField()  # audio_aggregate_content_score
    # questions = serializers.SerializerMethodField(source="question")
    questions = type(
        "SerializerMethodField",
        (serializers.SerializerMethodField, QuestionResponseSerializer),
        dict(),
    )(help_text="Get Questions List")
    # sales_qoutient
    # pace

    def audio_score(self, obj) -> AudioScore:
        return obj.audioscore_set.first()

    def score_per_question(self, obj) -> ScorePerQuestion:
        return obj.scoreperquestion_set.first()

    def audio_score_per_question(self, obj) -> AudioScorePerQuestion:
        return self.audio_score(obj).audioscoreperquestion_set.first()

    def text_score_per_question(self, obj) -> TextScorePerQuestion:
        return obj.textscoreperquestion_set.first()

    def get_likeabilty(self, obj):
        return self.score_per_question(obj).video_likeability

    def get_charm(self, obj):
        return self.score_per_question(obj).video_charm

    def get_energy(self, obj):
        return self.audio_score(obj).audio_energy

    def get_fluency(self, obj):
        return self.audio_score_per_question(obj).audio_fluency

    def get_confidence(self, obj):
        return self.audio_score_per_question(obj).audio_confidence

    def get_estimated_gesture_score(self, obj):
        return obj.video_estimated_gesture_score

    def get_sentiment_score(self, obj):
        return self.audio_score_per_question(obj).audio_sentiment_score

    def get_grammer_score(self, obj):
        return self.text_score_per_question(obj).question_grammer_score

    def get_volume(self, obj):
        return self.audio_score(obj).audio_volume

    def get_pitch(self, obj):
        return self.audio_score(obj).audio_pitch

    def get_content_score(self, obj):
        return self.audio_score(obj).audio_aggregate_content_score

    def get_questions(self, obj):
        question_ids = Score.objects.filter(interaction=obj.interaction).values_list(
            "question_id", flat=True
        )
        return QuestionResponseSerializer(
            instance=Response.objects.all(), many=True
        ).data

    class Meta:
        model = Score
        fields = "__all__"


class ProfileSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(required=False)
    institute_name = serializers.CharField(required=False)
    country = serializers.CharField(required=False)
    linkedin_url = serializers.CharField(required=False)
    facebook_url = serializers.CharField(required=False)
    twitter_url = serializers.CharField(required=False)
    instagram_url = serializers.CharField(required=False)

    def validate_email(self, attrs):
        user = self.context["request"].user
        user_ = User.objects.filter(email=attrs).exclude(id=user.id)
        if user_.count() > 0:
            raise serializers.ValidationError("This E-mail is already taken.")
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        # Update User Model
        User.objects.filter(id=user.id).update(
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            email=validated_data["email"],
        )
        UserDetail.objects.filter(user_id=user.id).update(
            phone_number=validated_data["phone_number"],
            institute_name=validated_data["institute_name"],
            country=validated_data["country"],
            linkedin_url=validated_data["linkedin_url"],
            facebook_url=validated_data["facebook_url"],
            twitter_url=validated_data["twitter_url"],
            instagram_url=validated_data["instagram_url"],
        )
        return {
            "first_name": validated_data["first_name"],
            "last_name": validated_data["last_name"],
            "email": validated_data["email"],
            "phone_number": validated_data["phone_number"],
            "institute_name": validated_data["institute_name"],
            "country": validated_data["country"],
            "linkedin_url": validated_data["linkedin_url"],
            "facebook_url": validated_data["facebook_url"],
            "twitter_url": validated_data["twitter_url"],
            "instagram_url": validated_data["instagram_url"],
        }

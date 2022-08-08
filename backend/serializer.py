from dataclasses import fields
from os import access

from backend.models import (Candidate, Interaction, Notification, Question,
                            Response, Test)
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db import models
from pyexpat import model
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated


# Register serializer
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "password", "first_name", "last_name", "email")
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

        return test


class FetchTestSerializer(serializers.Serializer):
    id = serializers.CharField(required=True)


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
            candidate_feedback=test,
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

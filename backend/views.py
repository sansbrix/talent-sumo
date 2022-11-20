from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.templatetags.static import static
from drf_yasg import openapi
from drf_yasg.openapi import TYPE_ARRAY, TYPE_OBJECT, TYPE_STRING, Schema
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.models import (Candidate, Interaction, Notification, Score, Test,
                            UserDetail, Response as ResponseModel, Question
                            )
from backend.utils import CreateCSVForInputAI, output_csv_ai

from .serializer import (CandidateSerializer, ChangePasswordSerializer,
                         FetchTestSerializer, IntrectionRatingSerializer,
                         NotificationSerializer, OutputCSVToAISerializer,
                         ProfileSerializer, QuestionSerializer,
                         ReportSerializer, ResponseSerializer, TestSerializer,
                         ValidateAccessCodeSerializer)


class TeamView(APIView):
    def get(self, request):
        return Response([])


# Create your views here.
class ChangePasswordView(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """

    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response(
                    {"old_password": ["Wrong password."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                "status": "success",
                "code": status.HTTP_200_OK,
                "message": "Password updated successfully",
                "data": [],
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateTestView(APIView, LimitOffsetPagination):
    permission_classes = (IsAuthenticated,)
    test_response = openapi.Response(
        "Interview Response Description", TestSerializer(many=True)
    )

    def add_fields_in_question(self, data, type_="create"):
        output = []
        for i in data["questions"]:
            i["updatedby"] = self.request.user.id
            i["createdby"] = self.request.user.id
            output.append(i)
        return output

    def add_fields_in_notifications(self, data, type_="create"):
        notifications = data["notification"]
        output = []
        for i in notifications:
            i["createdby"] = self.request.user.id
            i["updatedby"] = self.request.user.id
            output.append(i)
        return output

    def get_total_questions(self, data):
        return len(data["questions"])

    # Add Updated By And Created By
    @swagger_auto_schema(request_body=TestSerializer)
    def post(self, request, format=None):
        data = request.data
        data["questions"] = self.add_fields_in_question(request.data)
        data["notification"] = self.add_fields_in_notifications(request.data)
        data["total_question"] = self.get_total_questions(request.data)
        data["createdby"] = self.request.user.id
        data["updatedby"] = self.request.user.id

        serializer = TestSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(responses={200: test_response})
    def get(self, request, *args, **kwargs):
        search = self.request.query_params.get("search")
        if search:
            instance = Test.objects.filter(
                Q(job_title=search) | Q(track=search) 
                # | Q(id=search)
            ).filter(createdby=request.user.id)
        else:
            instance = Test.objects.filter(createdby=self.request.user)
        results = self.paginate_queryset(instance, request, view=self)
        data = TestSerializer(results, many=True).data
        return self.get_paginated_response(data)


class ReterieveTestView(generics.RetrieveAPIView, generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TestSerializer
    queryset = Test.objects.all()

    def retrieve(self, request, interviewId, *args, **kwargs):
        instance = get_object_or_404(Test, pk=interviewId)
        instance = TestSerializer(instance=instance)
        return Response(instance.data, status=status.HTTP_200_OK)

    def update(self, request, interviewId, *args, **kwargs):
        test_object = get_object_or_404(Test, pk=interviewId)
        self.instance_data = TestSerializer(instance=test_object).data
        data = request.data
        data["questions"] = self.add_fields_in_question(request.data, type_="update")
        data["notification"] = self.add_fields_in_notifications(
            request.data, type_="update"
        )
        data["total_question"] = self.get_total_questions(request.data)
        data["createdby"] = test_object.createdby.id
        data["updatedby"] = self.request.user.id

        serializer = TestSerializer(
            data=data, instance=test_object, context={"request": self.request}
        )
        if serializer.is_valid():
            serializer.update(instance=test_object, validated_data=data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def add_fields_in_question(self, data, type_="create"):
        output = []
        for i in data["questions"]:
            i["updatedby"] = self.request.user.id
            i["createdby"] = self.request.user.id
            output.append(i)
        return output

    def add_fields_in_notifications(self, data, type_="create"):
        notifications = data["notification"]
        output = []
        for i in notifications:
            i["createdby"] = self.request.user.id
            i["updatedby"] = self.request.user.id
            output.append(i)
        return output

    def get_total_questions(self, data):
        return len(data["questions"])


class ValidateAccessCode(generics.RetrieveAPIView):
    serializer_class = ValidateAccessCodeSerializer
    model = Test
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            object_ = Test.objects.filter(access_code=request.data["access_code"])
            data = {
                "is_exist": True if object_.count() > 0 else False,
                "data": TestSerializer(instance=object_.first()).data
                if object_.count() > 0
                else None,
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InteractionView(APIView, LimitOffsetPagination):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=CandidateSerializer)
    def post(self, request, *args, **kwargs):
        # response = request.data['response']
        serializer = CandidateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(query_serializer=FetchTestSerializer)
    def get(self, request, *args, **kwargs):
        search = self.request.query_params.get("search")
        if search:
            obj = Test.objects.filter(
                Q(job_title=search) | Q(track=search) | Q(id=search)
            ).filter(createdby=request.user.id)
        else:
            obj = Test.objects.filter(createdby=request.user.id)

        access_codes = obj.values_list("access_code", flat=True)
        candidates = Candidate.objects.filter(access_code__in=access_codes)
        results = self.paginate_queryset(candidates, request, view=self)
        serializer = CandidateSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)


class SingleTestIntrectionView(APIView, LimitOffsetPagination):
    permission_classes = (IsAuthenticated,)

    def get(self, request, testId, *args, **kwargs):
        test = Test.objects.filter(id=testId)
        if test.count() > 0:
            candidates = Candidate.objects.filter(access_code=test.first().access_code)
            results = self.paginate_queryset(candidates, request, view=self)
            serializer = CandidateSerializer(results, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            return Response(
                {"status": False, "message": "No Test is available with this ID"},
                status=status.HTTP_404_NOT_FOUND,
            )


class InputCSVToAIViewSet(APIView):
    def post(self, request, *args, **kwargs):
        try:
            obj = CreateCSVForInputAI()
            path = obj.create_csv()
            return Response(
                {
                    "path": request.build_absolute_uri("/media/output.csv"),
                    "status": True,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "message": "Something went wrong. Contact administrator",
                    "status": False,
                    "exception": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class OutputCSVToAIViewSet(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(request_body=OutputCSVToAISerializer)
    def post(self, request, *args, **kwargs):
        serializers = OutputCSVToAISerializer(data=request.FILES)
        if serializers.is_valid():
            request_file = request.FILES["file"] if "file" in request.FILES else None
            fs = FileSystemStorage()
            file = fs.save(request_file.name, request_file)
            fileurl = request.build_absolute_uri(fs.url(file))
            if output_csv_ai(fileurl):
                return Response(
                    {"message": "Your file has been uploaded to DB", "status": True},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "message": "Something went wrong. Contact administrator",
                        "status": False,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)


class ReportView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ReportSerializer
    queryset = Score.objects.all()

    def retrieve(self, request, intrectionId, *args, **kwargs):
        instance = ReportSerializer(
            instance=Score.objects.filter(interaction__id=intrectionId)
            .select_related("interaction")
            .prefetch_related(
                "audioscore_set",
                "audioscore_set__audioscoreperquestion_set",
                "scoreperquestion_set",
                "textscoreperquestion_set",
            ),
            many=True,
        )
        return Response(instance.data, status=status.HTTP_200_OK)


class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)
    profile_response = openapi.Response("Profile Response", ProfileSerializer)

    @swagger_auto_schema(
        request_body=ProfileSerializer, responses={200: profile_response}
    )
    def post(self, request, *args, **kwargs):
        profile_serializer = ProfileSerializer(
            data=request.data, context={"request": self.request}
        )
        if profile_serializer.is_valid():
            profile_serializer.save()
            return Response(profile_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(responses={200: profile_response})
    def get(self, request, *args, **kwargs):
        user_ = self.request.user
        user = User.objects.get(id=user_.id)
        user_details = UserDetail.objects.get(user_id=user_.id)
        response = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone_number": user_details.phone_number,
            "institute_name": user_details.institute_name,
            "country": user_details.country,
            "linkedin_url": user_details.linkedin_url,
            "facebook_url": user_details.facebook_url,
            "twitter_url": user_details.twitter_url,
            "instagram_url": user_details.instagram_url,
        }

        return Response(response, status=status.HTTP_200_OK)


class InteractionRatingView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=IntrectionRatingSerializer)
    def post(self, request, intrectionId, *args, **kwargs):
        serializer = IntrectionRatingSerializer(
            data=request.data, context={"request": self.request}
        )

        if serializer.is_valid():
            intraction = Interaction.objects.filter(id=intrectionId)
            if intraction.count() > 0:
                intraction.update(
                    start_rating=request.data.get("start_rating"),
                    rating_description=request.data.get("rating_description"),
                )
                return Response(
                    data={"message": "Intraction updated successfully."},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    data={"message": "Intraction not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FetchAllTestIds(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        tests = Test.objects.filter(createdby=request.user.id)
        return Response(data={"data" : tests.values_list("id", flat=True)})
    
    
class GetResponseById(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, pk, *args, **kwargs):
        candidate = Candidate.objects.get(id=pk)
        serializer = CandidateSerializer(instance=candidate)
        res = ResponseModel.objects.filter(candidate=candidate)
        data = []
        for i in res:
            temp = dict(ResponseSerializer(instance=i).data)
            # temp["questions"] = QuestionSerializer(instance=Question.objects.get(id=i.question_id)).data
            data.append(temp)
        intrection = Test.objects.filter(access_code=candidate.access_code).first()
        return Response(data={"data" : serializer.data, "responses": data, "intrection": TestSerializer(instance=intrection).data})
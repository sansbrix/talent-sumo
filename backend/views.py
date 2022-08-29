from backend.models import Candidate, Notification, Score, Test
from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import LimitOffsetPagination
from django.core.files.storage import FileSystemStorage
from backend.utils import CreateCSVForInputAI, output_csv_ai
from .serializer import (
    CandidateSerializer,
    ChangePasswordSerializer,
    FetchTestSerializer,
    NotificationSerializer,
    OutputCSVToAISerializer,
    QuestionSerializer,
    ReportSerializer,
    ResponseSerializer,
    TestSerializer,
    ValidateAccessCodeSerializer,
)
from django.templatetags.static import static

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

    def add_fields_in_question(self, data):
        output = []
        for i in data["questions"]:
            i["createdby"] = self.request.user.id
            i["updatedby"] = self.request.user.id
            output.append(i)
        return output

    def add_fields_in_notifications(self, data):
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

    @swagger_auto_schema(query_serializer=FetchTestSerializer)
    def get(self, request, *args, **kwargs):
        if self.request.GET.get("id"):
            instance = Test.objects.filter(id=self.request.GET.get("id"))
            if instance.count() > 0:
                data = TestSerializer(instance=instance.last()).data
                return Response(data=data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"status": False, "message": "No Test Found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            instance = Test.objects.filter(createdby=self.request.user)
            results = self.paginate_queryset(instance, request, view=self)
            data = TestSerializer(results, many=True).data
            return self.get_paginated_response(data)


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
            data = {
                "status": True,
            }
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(query_serializer=FetchTestSerializer)
    def get(self, request, *args, **kwargs):
        serializer = FetchTestSerializer(data=request.data)
        if serializer.is_valid():
            test = Test.objects.filter(id=request.data["id"])
            if test.count() > 0:
                candidates = Candidate.objects.filter(
                    access_code=test.first().access_code
                )
                results = self.paginate_queryset(candidates, request, view=self)
                serializer = CandidateSerializer(results, many=True)
                return self.get_paginated_response(serializer.data)
            else:
                return Response(
                    {"status": False, "message": "No Test is available with this ID"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

    def retrieve(self, request, intrectionId, *args, **kwargs):
        instance = ReportSerializer(
            instance=Score.objects.filter(id=1)
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

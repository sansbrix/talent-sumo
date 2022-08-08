from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

from backend.models import Candidate, Notification, Test
from .serializer import CandidateSerializer, ChangePasswordSerializer, FetchTestSerializer, NotificationSerializer, QuestionSerializer, ResponseSerializer, TestSerializer, ValidateAccessCodeSerializer
from rest_framework.permissions import IsAuthenticated

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
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class CreateTestView(APIView):
    permission_classes = (IsAuthenticated,)
    def add_fields_in_question(self, data):
        output = []
        for i in data['questions']:
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
        return len(data['questions'])

    # Add Updated By And Created By
    @swagger_auto_schema(request_body=TestSerializer) 
    def post(self, request, format=None):
        data = request.data
        data['questions'] = self.add_fields_in_question(request.data)
        data['notification'] = self.add_fields_in_notifications(request.data)
        data['total_question'] = self.get_total_questions(request.data)
        data['createdby'] = self.request.user.id
        data['updatedby'] = self.request.user.id
        
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
                return Response({
                    "status": False,
                    "message": "No Test Found"
                }, status=status.HTTP_404_NOT_FOUND)
        else:    
            instance = Test.objects.filter(createdby=self.request.user)
            data = TestSerializer(instance=instance, many=True).data
            return Response(data=data, status=status.HTTP_200_OK)
    
    
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
                "data": TestSerializer(instance=object_.first()).data if object_.count() > 0 else None 
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            

class InteractionView(APIView):
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
            test = Test.objects.filter(id=request.data['id'])
            if test.count() > 0:
                candidates = Candidate.objects.filter(access_code=test.first().access_code)
                serializer = CandidateSerializer(instance=candidates, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({
                    "status": False,
                    "message": "No Test is available with this ID"
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        
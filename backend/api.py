from django.contrib.auth.models import User
from rest_framework import generics, mixins, permissions, status
from rest_framework.response import Response

from .models import UserDetail

from .serializer import RegisterSerializer, UserSerializer


# Register API
class RegisterApi(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            if request.data.get("invitation_code"):
                code_exist = (
                    UserDetail.objects.filter(
                        invite_code=request.data["invitation_code"]
                    ).count()
                    > 0
                )
                if not code_exist:
                    return Response(
                        {
                            "message": "This invitation code doesn't exist.",
                            "status": False,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
        user = serializer.save()
        return Response(
            {
                "user": UserSerializer(
                    user, context=self.get_serializer_context()
                ).data,
                "message": "User Created Successfully.  Now perform Login to get your token",
            }
        )

from backend.views import (
    ChangePasswordView,
    CreateTestView,
    InputCSVToAIViewSet,
    InteractionView,
    OutputCSVToAIViewSet,
    ProfileView,
    ReportView,
    ReterieveTestView,
    SingleTestIntrectionView,
    ValidateAccessCode,
)
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt import views as jwt_views

from .api import RegisterApi

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version="v3",
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),
] + [
    path("docs", schema_view.as_view()),
    path("register", RegisterApi.as_view()),
    path("token/", jwt_views.TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", jwt_views.TokenRefreshView.as_view(), name="token_refresh"),
    path("change_password/", ChangePasswordView.as_view(), name="change_password"),
    path(
        "password_reset/",
        include("django_rest_passwordreset.urls", namespace="password_reset"),
    ),
    # Interview
    path("interview", CreateTestView.as_view()),
    path("interview/<str:interviewId>", ReterieveTestView.as_view()),
    path("validate-access-code", ValidateAccessCode.as_view()),
    path("interaction", InteractionView.as_view()),
    path("interaction/<str:testId>", SingleTestIntrectionView.as_view()),
    path("input-ai-csv", InputCSVToAIViewSet.as_view()),
    path("output-ai-csv", OutputCSVToAIViewSet.as_view()),
    path("report/<str:intrectionId>", ReportView.as_view()),
    path("profile", ProfileView.as_view()),
]

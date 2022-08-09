from django.contrib import admin
from django.urls import include, path
from django.conf import settings # to import static in deployment
from django.conf.urls.static import static # to import static in deployment

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("backend.urls")),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) # to import

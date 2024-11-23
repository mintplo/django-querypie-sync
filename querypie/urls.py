from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("companies/", include("company.urls")),
    path("admin/", admin.site.urls),
]

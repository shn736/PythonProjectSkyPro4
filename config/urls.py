from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("mailing_list_management.urls", namespace="mailing_list_management")),
    path("users/", include("users.urls", namespace="users")),
]

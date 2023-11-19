from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("base.urls", namespace="base")),
    path("login/accounts/", include("allauth.urls")),
    # Add more paths as needed
]

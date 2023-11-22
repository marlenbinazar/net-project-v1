from django.urls import path
from website import views

app_name = "base"

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="user_login"),
    path("logout/", views.user_logout, name="logout"),
    path("profile/", views.profile, name="profile"),
    path(
        "check_username_availability/",
        views.check_username_availability,
        name="check_username_availability",
    ),
    # Add more paths as needed
]

import pyrebase
from django.contrib import auth, messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from requests import HTTPError

from .firebase_utils import (
    get_user_data_from_firebase,
    get_user_token,
    login_user,
    register_user,
)


def register(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        # Call Firebase registration function
        user = register_user(email, password)
        if user:
            # Get the user token for further actions
            user_token = get_user_token(email, password)

            # You can store the user_token in session or cookie
            # or use it to fetch additional user details from Firebase

            return redirect("home")  # Redirect to the home page or any other view
        else:
            # Handle registration failure
            return render(request, "register.html", {"error": "Registration failed"})
        # Additional logic, such as creating a user profile in your Django models

    return render(request, "register.html")


def login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        # Call Firebase login function
        user = login_user(email, password)

        if user:
            # Get the user token for further actions
            user_token = get_user_token(email, password)

            # You can store the user_token in session or cookie
            # or use it to fetch additional user details from Firebase

            return redirect("home")  # Redirect to the home page or any other view
        else:
            # Handle login failure
            return render(request, "registration/login.html", {"error": "Login failed"})

    return render(request, "login.html")


def user_logout(request):
    # Handle user logout, clear the session, etc.
    logout(request)
    return redirect("home")


def profile(request):
    user_token = request.session.get(
        "user_token"
    )  # Get the user token from session or cookie

    if user_token:
        # Fetch user data from Firebase using the token
        # You can store this data in the context and pass it to the template
        context = {
            "user_data": get_user_data_from_firebase(user_token),
        }
        return render(request, "profile.html", context)
    else:
        # Handle unauthenticated user
        return redirect("login")

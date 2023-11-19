from django.contrib import auth, messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from requests import HTTPError

from .firebase_utils import login_and_get_user_data, register_user


def home(request):
    return render(request, "home.html")


def register(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        # Call Firebase registration and login function
        user = register_user(email, password)

        if user:
            # Use the combined function to get user data and token
            user_data, user_token = login_and_get_user_data(email, password)

            if user_data and user_token:
                # You can store the user_token in session or cookie
                # or use it to fetch additional user details from Firebase
                request.session["user_token"] = user_token

                return redirect("home")  # Redirect to the home page or any other view
            else:
                # Handle login failure
                return render(request, "register.html", {"error": "Login failed"})
        else:
            # Handle registration failure
            return render(request, "register.html", {"error": "Registration failed"})

        # Additional logic, such as creating a user profile in your Django models

    return render(request, "register.html")


def user_login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        # Call Firebase login and get user data function
        user_data, user_token = login_and_get_user_data(email, password)

        if user_data and user_token:
            # You can store the user_token in session or cookie
            # or use it to fetch additional user details from Firebase
            request.session["user_token"] = user_token

            return redirect("home")  # Redirect to the home page or any other view
        else:
            # Handle login failure
            return render(request, "login.html", {"error": "Login failed"})

    return render(request, "login.html")


def user_logout(request):
    # Clear any session variables related to Firebase
    if "user_token" in request.session:
        del request.session["user_token"]

    # Handle user logout, clear the session, etc.
    logout(request)

    return redirect("home")


@login_required
def profile(request):
    user_data, user_token = login_and_get_user_data(request)

    context = {
        "user_data": user_data,
    }
    return render(request, "profile.html", context)

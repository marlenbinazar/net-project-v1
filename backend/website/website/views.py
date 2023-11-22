from base.models import UserProfile
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect, render
from firebase_admin import auth, db

from .firebase_utils import authe, login_and_get_user_data, register_user


def home(request):
    return render(request, "home.html")


def register(request):
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        # Create a Django User instance
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )

        # Create a UserProfile object
        UserProfile.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
        )

        # Handle success message and email verification
        try:
            # Send email verification
            authe.send_email_verification(request.session["user_token"])

            return render(
                request,
                "login.html",
                {"message": "Please check your email to verify your account"},
            )
        except Exception as e:
            # Handle Firebase-related errors
            messages.error(request, f"Firebase error: {e}")
            return render(request, "login.html")

    return render(request, "login.html")


def check_username_availability(request):
    if request.method == "GET":
        username = request.GET.get("username", "")
        if not username:
            return JsonResponse({"error": "Username not provided"}, status=400)

        # Check if the username is already taken
        is_available = not UserProfile.objects.filter(username=username).exists()

        return JsonResponse({"is_available": is_available})

    return JsonResponse({"error": "Invalid request method"}, status=400)


def user_login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        # Call Firebase login and get user data function
        user_data, user_token = login_and_get_user_data(email, password)

        if user_data and user_token:
            if user_data.get("emailVerified"):
                request.session["user_token"] = user_token
                return redirect(
                    "profile"
                )  # Redirect to the home page or any other view
            else:
                # User is not verified, display a message
                messages.error(request, "Please verify your email to log in")
                return render(request, "login.html")
        else:
            # Handle login failure
            messages.error(request, "Login failed")
            return render(request, "login.html")

    return render(request, "login.html")


def user_logout(request):
    # Clear any session variables related to Firebase
    if "user_token" in request.session:
        del request.session["user_token"]

    return redirect("home")


@login_required
def profile(request):
    user_data, user_token = login_and_get_user_data(request)

    context = {
        "user_data": user_data,
    }
    return render(request, "profile.html", context)

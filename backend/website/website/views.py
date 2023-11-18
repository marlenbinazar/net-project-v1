from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import auth, messages
from django.contrib.auth import logout
from requests import HTTPError
import pyrebase
from django.urls import reverse

config = {
    'apiKey': "AIzaSyDeDn2g2FdM1U4ogovDQlnui7H1qjGL9iY",
    'authDomain': "netshards-dev.firebaseapp.com",
    'databaseURL': "https://netshards-dev-default-rtdb.europe-west1.firebasedatabase.app/",
    'projectId': "netshards-dev",
    'storageBucket': "netshards-dev.appspot.com",
    'messagingSenderId': "8675030171",
    'appId': "1:8675030171:web:b637a8d75862229f5ac23e",
    'measurementId': "G-MCLPQFXBDF"
}

firebase = pyrebase.initialize_app(config)
authe = firebase.auth()
database = firebase.database()
def index(request):
    return render(request, "index.html")

def user_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = authe.sign_in_with_email_and_password(email, password)
            if user is not None:
                session_id = user['idToken']
                request.session['uid'] = str(session_id)
                """ messages.success(request, "You logged in") """
                email = request.POST.get('email')
                profile_url = reverse('profile')
                return redirect(f'{profile_url}?email={email}')
        except HTTPError as e:
            if e.response is not None and e.response.status_code == 400:
                error_message = e.response.json().get('error', {}).get('message')
                messages.error(request, f"Login failed: {error_message}")
                return render(request, 'login.html', {'error_message': error_message})
            else:
                messages.error(request, "Invalid login credentials")
                return render(request, 'login.html', {'error_message': "Invalid login credentials"})

    return render(request, "login.html")

def signup(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = authe.create_user_with_email_and_password(email, password)
        except:
            messages.error(request, "You successfully signed up")
            return render(request, 'signup.html') 

        uid = user['localId']

        data = {
            "name":name, 
            "status":"1"
        }

        database.child("users").child(uid).child("details").set(data)
        messages.success(request, "You successfully signed up")
        return redirect('login')

    return render(request, 'signup.html')

def user_logout(request):
    logout(request)
    return redirect('login')

def profile(request):
    email = request.GET.get('email', '')
    context = {'email': email}
    return render(request, 'profile.html', context)





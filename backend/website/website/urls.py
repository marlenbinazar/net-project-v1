from django.contrib import admin
from django.urls import path
from .views import user_login, user_logout, profile, signup, index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='user_logout'),
    path('profile/', profile, name='profile'),
    path('signup/', signup, name='signup'),
]

from django.urls import path
from apps.authentication.views import login, register, current_user

app_name = 'authentication'

urlpatterns = [
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('current-user/', current_user, name='current_user'),
]
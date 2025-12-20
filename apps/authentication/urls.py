from django.urls import path
from apps.authentication.views import login, register, logout, current_user 

app_name = 'authentication'

urlpatterns = [
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout, name='logout'),
    path('current-user/', current_user, name='current_user')
]
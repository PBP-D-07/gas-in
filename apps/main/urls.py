from apps.main.views import show_main, register_user, login_user, get_all_user
from django.urls import path

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('users/', get_all_user, name='get_all_user')
]

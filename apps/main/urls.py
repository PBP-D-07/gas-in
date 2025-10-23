from apps.main.views import show_main, register_user, login_user, get_all_user,show_login, logout_user
from django.urls import path

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('register/', register_user, name='register'),
    path('api/login/', login_user, name='login'),
    path('api/logout/', logout_user, name='logout'),
    path('login/', show_login, name='show_login'),
    path('users/', get_all_user, name='get_all_user')
]
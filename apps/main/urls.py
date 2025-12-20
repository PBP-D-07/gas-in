from apps.main.views import show_main, register_user, login_user, get_all_user,show_login, logout_user, show_register, promote_to_admin, demote_from_admin, proxy_image
from django.urls import path

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('register/', show_register, name='register'),
    path('api/register/', register_user, name='api_register'),
    path('api/login/', login_user, name='login'),
    path('api/logout/', logout_user, name='logout'),
    path('login/', show_login, name='show_login'),
    path('users/', get_all_user, name='get_all_user'),
    path('api/promote-admin/', promote_to_admin, name='promote_admin'),
    path('api/demote-admin/', demote_from_admin, name='demote_admin'),
    path('api/proxy-image/', proxy_image, name='proxy_image'),
]

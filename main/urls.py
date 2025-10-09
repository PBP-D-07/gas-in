from main.views import show_main, register
from django.urls import path

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('register/', register, name='register')
]

from .views import show_main
from django.urls import path

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    
]

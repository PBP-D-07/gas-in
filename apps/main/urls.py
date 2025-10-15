from apps.main.views import show_main, register
from django.urls import path

# import views dari module venue
from apps.venueModule.views import show_venue, venue_detail

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('register/', register, name='register'),
    path('venues/', show_venue, name='show_venue'),
    path('venues/<int:venue_id>/', venue_detail, name='venue_detail'),
]
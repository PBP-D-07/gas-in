from django.urls import path
from .views import show_venue, venue_detail

app_name = 'venue'

urlpatterns = [
	path('', show_venue, name='show_venue'),
	path('<int:venue_id>/', venue_detail, name='venue_detail'),
]
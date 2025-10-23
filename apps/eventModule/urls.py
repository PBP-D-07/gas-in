from django.urls import path
from apps.eventModule.views import (
    show_discover,
    get_filtered_events,
    get_filter_options
)

app_name = 'eventModule'

urlpatterns = [
    # Halaman discovery
    path('', show_discover, name='show_discover'),
    
    # API endpoints
    path('api/events/', get_filtered_events, name='get_filtered_events'),
    path('api/filter-options/', get_filter_options, name='get_filter_options'),
]
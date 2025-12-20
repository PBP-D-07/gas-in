from django.urls import path
from apps.eventModule.views import (
    show_discover,
    show_saved_searches,
    get_filtered_events,
    get_filter_options,
    
    # Saved Search CRUD
    create_saved_search,
    get_saved_searches,
    get_saved_search_by_id,
    update_saved_search,
    delete_saved_search,
)

app_name = 'eventModule'

urlpatterns = [
    # Halaman discovery
    path('', show_discover, name='show_discover'),
    path('saved-searches/', show_saved_searches, name='show_saved_searches'),
    
    # API endpoints - Discovery
    path('api/events/', get_filtered_events, name='get_filtered_events'),
    path('api/filter-options/', get_filter_options, name='get_filter_options'),
    
    # API endpoints - Saved Search CRUD
    path('api/saved-search/create/', create_saved_search, name='create_saved_search'),
    path('api/saved-search/', get_saved_searches, name='get_saved_searches'),
    path('api/saved-search/<uuid:id>/', get_saved_search_by_id, name='get_saved_search_by_id'),
    path('api/saved-search/<uuid:id>/update/', update_saved_search, name='update_saved_search'),
    path('api/saved-search/<uuid:id>/delete/', delete_saved_search, name='delete_saved_search'),
]
from django.urls import path
from apps.eventMakerModule.views import create_event, show_create, show_edit, get_all_event,get_event_by_id, delete_event, edit_event

app_name = 'eventMakerModule'

urlpatterns = [
    path("api/create/", create_event, name="create_event"),
    path("api/delete/<uuid:id>/", delete_event, name="delete_event"),
    path("api/edit/<uuid:id>/", edit_event, name="edit_event"),
    path("create/",show_create, name="show_create"),
    path("edit/<uuid:id>/",show_edit, name="show_edit"),
    path("all/", get_all_event, name="get_all_event"),
    path("<uuid:id>/", get_event_by_id, name="get_event_by_id"),
]

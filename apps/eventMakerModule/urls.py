from django.urls import path
from apps.eventMakerModule.views import create_event, show_create, get_all_event, delete_event

app_name = 'eventMakerModule'

urlpatterns = [
    path("api/create/", create_event, name="create_event"),
    path("create/",show_create, name="show_create" ),
    path("all/", get_all_event, name="get_all_event"),
    path("delete/<uuid:id>", delete_event, name="delete_event")
]

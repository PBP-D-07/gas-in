from django.urls import path
from apps.eventMakerModule.views import create_event, show_create

urlpatterns = [
    path("api/create/", create_event, name="create_event"),
    path("create/",show_create, name="show_create" )
]

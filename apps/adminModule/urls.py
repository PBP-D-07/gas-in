from django.urls import path
from apps.adminModule.views import dashboard, update_event_status, delete_event, dashboard_json

app_name = 'adminModule'

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('json/', dashboard_json, name='dashboard_json'),
    path('events/update-status/<uuid:event_id>/', update_event_status, name='update_event_status'),
    path('events/delete/<uuid:event_id>/', delete_event, name='delete_event'),
]


from django.urls import path
from .views import show_venue, venue_detail, show_json_venue, show_xml_venue, show_json_by_id_venue, show_xml_by_id_venue

app_name = 'venue'

urlpatterns = [
	path('', show_venue, name='show_venue'),
    path('api/json/', show_json_venue, name='show_json_venue'),
	path('api/xml/', show_xml_venue, name='show_xml_venue'),
	path('<uuid:venue_id>/', venue_detail, name='venue_detail'),
	path('api/json/<uuid:venue_id>/', show_json_by_id_venue, name='show_json_by_id_venue'),
	path('api/xml/<uuid:venue_id>/', show_xml_by_id_venue, name='show_xml_by_id_venue'),
]
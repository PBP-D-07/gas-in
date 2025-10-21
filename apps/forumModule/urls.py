from django.urls import path
from apps.forumModule.views import show_main, create_post, show_post, show_xml, show_json, show_xml_by_id, show_json_by_id, edit_post

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('create-post/', create_post, name='create_post'),
    path('post/<str:id>/', show_post, name='show_post'),
    path('xml/', show_xml, name='show_xml'),
    path('json/', show_json, name='show_json'),
    path('xml/<str:news_id>/', show_xml_by_id, name='show_xml_by_id'),
    path('json/<str:news_id>/', show_json_by_id, name='show_json_by_id'),
    path('post/<uuid:id>/edit', edit_post, name='edit_post'),
]

from django.urls import path
from apps.forumModule.views import show_main, create_post, edit_post, delete_post, show_post, show_json, show_json_by_id

app_name = 'forumModule'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('create-post/', create_post, name='create_post'),
    path('edit/<str:id>/', edit_post, name='edit_post'),
    path('delete/<str:id>/', delete_post, name='delete_post'),
    path('json/', show_json, name='show_json'),
    path('json/<str:post_id>/', show_json_by_id, name='show_json_by_id'),
    path('<str:post_id>/', show_post, name='show_post'),
]

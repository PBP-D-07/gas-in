from django.urls import path
from apps.forumModule.views import show_main, create_post, edit_post, delete_post

app_name = 'forumModule'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('create-post/', create_post, name='create_post'),
    path('post/<uuid:id>/edit', edit_post, name='edit_post'),
    path('post/<uuid:id>/delete', delete_post, name='delete_post'),
]

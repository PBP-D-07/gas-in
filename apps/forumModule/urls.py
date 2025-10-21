from django.urls import path
from apps.forumModule.views import show_main, create_post, show_post, edit_post

app_name = 'forumModule'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('create-post/', create_post, name='create_post'),
    path('post/<str:id>/', show_post, name='show_post'),
    path('post/<uuid:id>/edit', edit_post, name='edit_post'),
]

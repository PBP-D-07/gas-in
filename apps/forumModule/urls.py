from django.urls import path
from apps.forumModule import views
from django.contrib import admin 

app_name = 'forumModule'

urlpatterns = [
    path('admin-django/', admin.site.urls),
    path('', views.show_main, name='show_main'),
    path('create/', views.create_post, name='create_post'),
    path('json/', views.show_json, name='show_json'),
    path('like/<str:post_id>/', views.toggle_like, name='toggle_like'), 
    path('comment/<str:post_id>/', views.get_comments, name='get_comments'),
    path('comment/<str:post_id>/add/', views.add_comment, name='add_comment'),
    path('json/<str:post_id>/', views.show_json_by_id, name='show_json_by_id'),
    path('edit/<str:id>/', views.edit_post, name='edit_post'),
    path('delete/<str:id>/', views.delete_post, name='delete_post'),
    path('check-like/<str:post_id>/', views.check_user_liked, name='check_user_liked'),
    path('<str:post_id>/', views.show_post, name='show_post'), 
]
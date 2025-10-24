# from django.urls import path
# from apps.forumModule.views import add_comment, get_comments, show_main, create_post, edit_post, delete_post, show_post, show_json, show_json_by_id, toggle_like


# app_name = 'forumModule'

# urlpatterns = [
#     path('', show_main, name='show_main'),
#     path('create-post/', create_post, name='create_post'),
#     path('edit/<str:id>/', edit_post, name='edit_post'),
#     path('delete/<str:id>/', delete_post, name='delete_post'),
#     path('json/<str:post_id>/', show_json_by_id, name='show_json_by_id'),
#     path('json/', show_json, name='show_json'),
#     path('<str:post_id>/', show_post, name='show_post'),
#     path('like/<uuid:post_id>/', toggle_like, name='toggle_like'),
#     path("comment/<str:post_id>/", get_comments, name="get_comments"),
#     path("comment/<str:post_id>/add/", add_comment, name="add_comment"),
# ]
from django.urls import path
from apps.forumModule import views

app_name = 'forumModule'

urlpatterns = [
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
from django.contrib import admin
from .models import Post, Comment

# Register your models here.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'owner', 'post_views', 'like_count', 'created_at', 'is_post_hot')
    list_filter = ('category', 'created_at', 'owner')
    search_fields = ('description', 'owner__username')
    readonly_fields = ('post_views', 'like_count', 'id')
    ordering = ('-created_at',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'author', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('content', 'author__username')
    ordering = ('-created_at',)
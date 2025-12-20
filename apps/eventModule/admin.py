from django.contrib import admin
from apps.eventModule.models import SavedSearch

@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'location', 'category', 'created_at')
    list_filter = ('location', 'category', 'created_at')
    search_fields = ('name', 'user__username', 'location')
    readonly_fields = ('id', 'created_at')
    ordering = ('-created_at',)
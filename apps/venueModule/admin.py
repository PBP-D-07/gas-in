from django.contrib import admin
from .models import Venue, VenueImage

class VenueImageInline(admin.TabularInline):
    model = VenueImage
    extra = 1

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
	list_display = ('name', 'category', 'location', 'owner')
	inlines = [VenueImageInline]


@admin.register(VenueImage)
class VenueImageAdmin(admin.ModelAdmin):
	list_display = ('venue', 'image', 'order')
	ordering = ('order',)
	search_fields = ('venue__name', 'image')
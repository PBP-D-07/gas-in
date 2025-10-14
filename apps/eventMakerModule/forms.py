from django.forms import ModelForm
from apps.eventMakerModule.models import Event
from django.utils.html import strip_tags

class EventForm(ModelForm):
    class Meta:
        model = Event
        fields = ["name", "description", "date", "location", "category", "thumbnail", "created_at"]
        
    def clean_name(self):
        name = self.cleaned_data["name"]
        return strip_tags(name)

    def clean_description(self):
        description = self.cleaned_data["description"]
        return strip_tags(description)
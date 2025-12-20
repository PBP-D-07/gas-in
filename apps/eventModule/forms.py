from django.forms import ModelForm
from apps.eventModule.models import SavedSearch
from django.utils.html import strip_tags

class SavedSearchForm(ModelForm):
    class Meta:
        model = SavedSearch
        fields = ["name", "location", "category"]
    
    def clean_name(self):
        name = self.cleaned_data["name"]
        return strip_tags(name)
    
    def clean_location(self):
        location = self.cleaned_data.get("location")
        if location:
            return strip_tags(location)
        return location
    
    def clean_category(self):
        category = self.cleaned_data.get("category")
        if category:
            return strip_tags(category)
        return category
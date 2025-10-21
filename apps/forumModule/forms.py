from django.forms import ModelForm
from .models import Post
from django.utils.html import strip_tags

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content"]

    def clean_name(self):
        name = self.cleaned_data["name"]
        return strip_tags(name)

    def clean_description(self):
        description = self.cleaned_data["description"]
        return strip_tags(description)


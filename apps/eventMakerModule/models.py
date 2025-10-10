from django.db import models
from apps.main.models import User
from uuid import uuid4

# Create your models here.
class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=255) # wajib input
    date = models.DateTimeField() # wajib input
    location = models.CharField(max_length=255) # wajib input
    thumbnail = models.ImageField(upload_to='event_thumbnails/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='owned_events')
    participants = models.ManyToManyField(User, related_name='joined_events', blank=True)

    def __str__(self):
        return self.title
from django.db import models
from apps.main.models import User
from uuid import uuid4

# Create your models here.
class Event(models.Model):
    CATEGORY_CHOICES = [
    ('running', 'Lari'),
    ('badminton', 'Badminton'),
    ('futsal', 'Futsal'),
    ('football', 'Sepak Bola'),
    ('basketball', 'Basket'),
    ('cycling', 'Sepeda'),
    ('volleyball', 'Voli'),
    ('yoga', 'Yoga'),
    ('padel', 'Padel'),
    ('other', 'Lainnya'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255) # wajib input
    description = models.TextField(default="No description available") # wajib input
    date = models.DateTimeField() # wajib input
    location = models.CharField(max_length=255) # wajib input
    thumbnail = models.ImageField(upload_to='event_thumbnails/', blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    created_at = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='owned_events')
    participants = models.ManyToManyField(User, related_name='joined_events', blank=True)

    def __str__(self):
        return self.name
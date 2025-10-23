import uuid
from django.conf import settings
from django.db import models
from apps.main.models import User

class Venue(models.Model):
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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255)
    thumbnail = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='other')
    created_at = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)
    contact_number = models.CharField(max_length=12, blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='owned_venues')

    def __str__(self):
        return f"{self.name} ({self.category}) - {self.location}"
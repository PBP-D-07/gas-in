import uuid
from django.conf import settings
from django.db import models

class Venue(models.Model):
    CATEGORY_CHOICES = [
        ('concert', 'Concert'),
        ('sports', 'Sports'),
        ('theater', 'Theater'),
        ('conference', 'Conference'),
        ('exhibition', 'Exhibition'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255)
    thumbnail = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='other')
    created_at = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.category}) - {self.location}"
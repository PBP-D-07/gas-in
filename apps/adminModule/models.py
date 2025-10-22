from django.db import models
from django.contrib.auth.models import User
from uuid import uuid4
from apps.eventMakerModule.models import Event

class Admin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


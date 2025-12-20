from django.db import models
from apps.main.models import User
from uuid import uuid4

class SavedSearch(models.Model):
    """Model untuk menyimpan pencarian/filter favorit user"""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_searches')
    name = models.CharField(max_length=100)  # Nama untuk saved search, e.g. "Futsal Jakarta"
    location = models.CharField(max_length=255, blank=True, default='')
    category = models.CharField(max_length=20, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Saved Searches"
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"
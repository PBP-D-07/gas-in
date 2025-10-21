from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=200)          
    content = models.TextField()                     
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True) 
    post_views = models.PositiveIntegerField(default=0) 
    created_at = models.DateTimeField(auto_now_add=True)        
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return self.title
    
    @property
    def is_post_hot(self):
        return self.post_views > 20
    
    def increment_views(self):
        self.post_views += 1
        self.save()

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"


from django.db import models
from .managers import PostManager


class Post(models.Model):
    author_id = models.CharField(max_length=255)
    author_name = models.CharField(max_length=255)
    title = models.CharField(max_length=200)
    text = models.TextField()
    image = models.TextField()
    thumbnail = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = PostManager()

    def __str__(self):
        return f"{self.title} by {self.author_name}"

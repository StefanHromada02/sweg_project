from django.db import models
from .managers import CommentManager


class Comment(models.Model):
    author_id = models.CharField(max_length=255)
    author_name = models.CharField(max_length=255)
    post = models.ForeignKey(
        'posts.Post',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CommentManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.author_name} on {self.post.title}"

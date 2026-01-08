from django.db import models
from django.db.models import QuerySet


class CommentQuerySet(QuerySet):
    """QuerySet methods for Comment model, to enable chaining."""

    def by_post(self, post_id):
        """Filter comments by post."""
        return self.filter(post_id=post_id)

    def newest_first(self):
        """Orders comments by creation date, newest first."""
        return self.order_by('-created_at')


class CommentManager(models.Manager):
    """Custom Manager that uses the custom QuerySet."""
    def get_queryset(self):
        return CommentQuerySet(self.model, using=self._db)
        return self.get_queryset().with_relations()
    
    def by_user(self, user_id):
        """Filter comments by user."""
        return self.get_queryset().by_user(user_id)
    
    def by_post(self, post_id):
        """Filter comments by post."""
        return self.get_queryset().by_post(post_id)

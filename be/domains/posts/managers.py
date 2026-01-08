# posts/managers.py
from django.db import models
from django.db.models import QuerySet

class PostQuerySet(QuerySet):
    """QuerySet methods for Post model, to enable chaining."""

    def with_author(self):
        """Pre-fetches the related User object."""
        # Django's equivalent of SQLAlchemy's joinedload: select_related
        return self.select_related('user')

    def newest_first(self):
        """Orders posts by creation date, newest first."""
        # Das Minuszeichen '-' bewirkt die absteigende Sortierung (desc)
        return self.order_by('-created_at')

class PostManager(models.Manager):
    """Custom Manager that uses the custom QuerySet."""
    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db)
    
    def with_author(self):
        """Pre-fetches the related User object."""
        return self.get_queryset().with_author()
    
    def newest_first(self):
        """Orders posts by creation date, newest first."""
        return self.get_queryset().newest_first()

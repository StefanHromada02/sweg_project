from rest_framework import serializers
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "post", "text", "created_at", "author_id", "author_name"]
        read_only_fields = ["created_at", "author_id", "author_name"]


class CommentCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating comments."""
    class Meta:
        model = Comment
        fields = ["id", "post", "text", "created_at", "author_id", "author_name"]
        read_only_fields = ["created_at", "author_id", "author_name"]

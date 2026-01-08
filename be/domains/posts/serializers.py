from rest_framework import serializers
from .models import Post
from django.conf import settings


class PostSerializer(serializers.ModelSerializer):
    # Akzeptiert Upload von Bild-Dateien
    image_file = serializers.ImageField(write_only=True, required=False)
    # URL-Pfad wird automatisch gesetzt (read-only)
    image = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    # Comment count
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ["id", "author_id", "author_name", "title", "text", "image", "thumbnail", "image_file", "created_at", "comment_count"]
        read_only_fields = ["author_id", "author_name", "image", "thumbnail"]

    def get_image(self, obj):
        if obj.image:
            return f"{settings.MEDIA_URL}{obj.image}"
        return None

    def get_thumbnail(self, obj):
        if obj.thumbnail:
            return f"{settings.MEDIA_URL}{obj.thumbnail}"
        return None

    def get_comment_count(self, obj):
        """Return the number of comments for this post."""
        return obj.comments.count()

    def validate_image_file(self, value):
        """Validiere Bildgröße und Format."""
        # Max 5MB
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Image size must be less than 5MB")

        # Erlaubte Formate
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError(
                f"Only JPEG, PNG, GIF, and WebP images are allowed"
            )

        return value

    def create(self, validated_data):
        """Remove image_file from validated_data before creating Post."""
        validated_data.pop('image_file', None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Remove image_file from validated_data before updating Post."""
        validated_data.pop('image_file', None)
        return super().update(instance, validated_data)
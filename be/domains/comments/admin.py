from django.contrib import admin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "author_name",
        "post",
        "text_preview",
        "created_at"
    )

    list_filter = (
        "created_at",
        "author_name",
        "post"
    )

    search_fields = (
        "text",
        "author_name",
        "post__title"
    )

    readonly_fields = (
        "created_at",
    )

    def text_preview(self, obj):
        """Show first 50 characters of comment text."""
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text
    text_preview.short_description = "Text"

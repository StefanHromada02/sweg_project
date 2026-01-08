from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # Felder, die in der Admin-Liste angezeigt werden
    list_display = (
        "title",
        "author_name",
        "created_at"
    )

    # Filtern nach User und Datum
    list_filter = (
        "author_name",
        "created_at"
    )

    # Felder, die durchsucht werden können (mit ForeignKey-Lookup)
    search_fields = (
        "title",
        "text",
        "author_name"
    )

    # Die Erstellungszeit sollte nicht im Bearbeitungsformular geändert werden
    readonly_fields = (
        "created_at",
    )
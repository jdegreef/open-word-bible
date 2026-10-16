from django.contrib import admin

from .models import ReaderMessage


@admin.register(ReaderMessage)
class ReaderMessageAdmin(admin.ModelAdmin):
    list_display = ["created_at", "kind", "verse", "language", "status"]
    list_filter = ["status", "kind", "language"]
    search_fields = ["verse", "text"]
    raw_id_fields = ["user", "replied_by"]

from django.contrib import admin

from .models import Handoff, Like, Saved


@admin.register(Handoff)
class HandoffAdmin(admin.ModelAdmin):
    list_display = ("user", "site", "created_at", "used_at")
    readonly_fields = ("user", "site", "code_hash", "created_at", "used_at")


@admin.register(Saved, Like)
class MarkAdmin(admin.ModelAdmin):
    list_display = ("key", "user", "created_at")
    search_fields = ("key", "user__username")
    raw_id_fields = ("user",)

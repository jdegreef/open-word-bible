from django.contrib import admin

from .models import GroupPost, Membership, ReadingGroup


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 0
    raw_id_fields = ["user"]


@admin.register(ReadingGroup)
class ReadingGroupAdmin(admin.ModelAdmin):
    list_display = ["name", "plan_id", "created_at"]
    search_fields = ["name"]
    exclude = ["invite_code"]
    inlines = [MembershipInline]


@admin.register(GroupPost)
class GroupPostAdmin(admin.ModelAdmin):
    """Kept for removing a post that breaks the terms of use."""
    list_display = ["group", "day", "user", "created_at"]
    raw_id_fields = ["user", "group"]

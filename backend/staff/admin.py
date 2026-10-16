from django.contrib import admin

from .models import AdminAction, Broadcast


@admin.register(AdminAction)
class AdminActionAdmin(admin.ModelAdmin):
    list_display = ["created_at", "actor_email", "action", "target"]
    list_filter = ["action"]
    search_fields = ["actor_email", "target"]
    readonly_fields = ["actor", "actor_email", "action", "target", "detail", "created_at"]

    def has_add_permission(self, request):
        return False


@admin.register(Broadcast)
class BroadcastAdmin(admin.ModelAdmin):
    list_display = ["sent_at", "subject", "audience", "recipients", "failed"]
    readonly_fields = ["subject", "body", "audience", "recipients", "failed", "sent_by", "sent_at"]

    def has_add_permission(self, request):
        return False

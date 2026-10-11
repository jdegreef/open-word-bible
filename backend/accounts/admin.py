from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import ApiToken, Role, SavedVerse, SignInLink

User = get_user_model()


class RoleInline(admin.TabularInline):
    model = Role
    fk_name = "user"
    extra = 0
    fields = ["kind", "language", "granted_by", "created_at"]
    readonly_fields = ["granted_by", "created_at"]


class ApiTokenInline(admin.TabularInline):
    model = ApiToken
    extra = 0
    fields = ["label", "created_at", "last_used_at"]
    readonly_fields = fields
    verbose_name = "signed-in device"

    def has_add_permission(self, request, obj=None):
        return False


admin.site.unregister(User)


@admin.register(User)
class AccountAdmin(UserAdmin):
    """Users with their roles and signed-in devices. Deleting a device signs
    it out."""
    inlines = [RoleInline, ApiTokenInline]
    list_display = ["email", "first_name", "role_list", "date_joined", "last_login", "is_active"]
    list_filter = ["roles__kind", "is_active"]
    search_fields = ["email", "first_name"]
    ordering = ["-date_joined"]

    @admin.display(description="Roles")
    def role_list(self, user):
        return ", ".join(str(r) for r in user.roles.all()) or "Reader"

    def save_formset(self, request, form, formset, change):
        for role in formset.save(commit=False):
            if isinstance(role, Role) and role.granted_by_id is None:
                role.granted_by = request.user
            role.save()
        for obj in formset.deleted_objects:
            obj.delete()
        formset.save_m2m()


@admin.register(SignInLink)
class SignInLinkAdmin(admin.ModelAdmin):
    list_display = ["email", "created_at", "used_at", "requested_ip"]
    search_fields = ["email"]
    readonly_fields = ["email", "token_hash", "created_at", "used_at", "requested_ip"]

    def has_add_permission(self, request):
        return False


@admin.register(SavedVerse)
class SavedVerseAdmin(admin.ModelAdmin):
    list_display = ["user", "verse", "kind", "colour", "updated_at"]
    list_filter = ["kind", "colour"]
    search_fields = ["user__username", "verse"]

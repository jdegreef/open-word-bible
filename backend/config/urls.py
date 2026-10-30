from django.contrib import admin
from django.urls import include, path

from accounts import controls, google, passkeys
from accounts import views as accounts
from api import views
from feedback import views as feedback
from groups import views as groups

admin.site.site_header = "Open Word Bible"
admin.site.site_title = "Open Word Bible admin"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/editions/", views.editions),
    path("api/text/<str:book>/<int:chapter>/", views.chapter_text),
    path("api/passages/<str:book>/<int:chapter>/", views.passages),
    path("api/search/", views.search),
    path("api/auth/methods", accounts.methods),
    path("api/auth/sign-in", accounts.sign_in),
    path("api/auth/sign-up", accounts.sign_up),
    path("api/auth/link", accounts.request_link),
    path("api/auth/verify", accounts.verify),
    path("api/auth/reset", accounts.request_reset),
    path("api/auth/reset/confirm", accounts.confirm_reset),
    path("api/auth/google/start", google.start),
    path("api/auth/google/callback", google.callback),
    path("api/auth/sign-out", accounts.sign_out),
    path("api/auth/passkey/options", passkeys.sign_in_options),
    path("api/auth/passkey", passkeys.sign_in),
    path("api/me", accounts.me),
    path("api/me/devices", controls.devices),
    path("api/me/devices/sign-out-others", controls.sign_out_others),
    path("api/me/devices/<int:token_id>", controls.device),
    path("api/me/email", controls.change_email),
    path("api/me/email/confirm", controls.confirm_email),
    path("api/me/prefs", controls.prefs),
    path("api/me/passkeys/options", passkeys.register_options),
    path("api/me/passkeys", passkeys.passkeys),
    path("api/me/passkeys/<int:passkey_id>", passkeys.passkey),
    path("api/email/unsubscribe", controls.unsubscribe),
    path("api/groups", groups.groups),
    path("api/groups/invite/<str:code>", groups.invite),
    path("api/groups/join", groups.join),
    path("api/groups/<int:group_id>", groups.group),
    path("api/groups/<int:group_id>/leave", groups.leave),
    path("api/groups/<int:group_id>/invite", groups.new_invite),
    path("api/groups/<int:group_id>/members/<int:member_id>", groups.member),
    path("api/groups/<int:group_id>/posts", groups.posts),
    path("api/groups/<int:group_id>/posts/<int:post_id>", groups.post),
    path("api/reading", accounts.reading),
    path("api/messages", feedback.messages),
    path("api/admin/", include("staff.urls")),
    path("healthz", views.healthz),
]

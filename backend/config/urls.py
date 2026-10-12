from django.contrib import admin
from django.urls import path

from accounts import google
from accounts import views as accounts
from api import views

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
    path("api/me", accounts.me),
    path("healthz", views.healthz),
]

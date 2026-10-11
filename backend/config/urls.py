from django.contrib import admin
from django.urls import path

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
    path("api/auth/link", accounts.request_link),
    path("api/auth/verify", accounts.verify),
    path("api/auth/sign-out", accounts.sign_out),
    path("api/me", accounts.me),
    path("api/saved", accounts.saved),
    path("api/saved/<str:verse>/<str:kind>", accounts.saved_verse),
    path("healthz", views.healthz),
]

from django.contrib import admin
from django.urls import path

from api import views

admin.site.site_header = "Open Word Bible"
admin.site.site_title = "Open Word Bible admin"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/editions/", views.editions),
    path("api/text/<str:book>/<int:chapter>/", views.chapter_text),
    path("api/passages/<str:book>/<int:chapter>/", views.passages),
    path("healthz", views.healthz),
]

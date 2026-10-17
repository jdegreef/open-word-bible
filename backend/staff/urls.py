from django.urls import path

from . import articles, emails, export, fixes, inbox, jobs, progress, team, text, users, verses

urlpatterns = [
    path("overview/", progress.overview),
    path("coverage/", progress.coverage),
    path("languages/", progress.language_list),
    path("books/<str:code>/", progress.book),
    path("health/", progress.health),
    path("engagement/", progress.engagement),
    path("inbox/", inbox.inbox),
    path("inbox/<int:message_id>/", inbox.message),
    path("users/", users.user_list),
    path("users/<int:user_id>/", users.user_detail),
    path("users/<int:user_id>/sign-out/", users.sign_out),
    path("verses/", verses.find),
    path("verses/<str:vid>/", verses.verse),
    path("fixes/", fixes.fixes),
    path("decisions/", text.decisions),
    path("terms/", text.terms),
    path("articles/", articles.articles),
    path("export/", export.options),
    path("export/preview/", export.preview),
    path("export/file/", export.download),
    path("emails/", emails.emails),
    path("jobs/", jobs.jobs),
    path("team/", team.team),
    path("team/roles/<int:role_id>/", team.revoke),
    path("team/invite/", team.resend),
    path("activity/", team.activity),
]

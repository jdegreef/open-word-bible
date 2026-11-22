"""The admin's own records: what was done in it, and the emails it sent."""
from django.conf import settings
from django.db import models


class AdminAction(models.Model):
    """One thing done in the admin: a role granted or removed, an account
    deleted, a job filed, an email sent, a reader answered. Reviews have
    their own trail (translation.ReviewEvent). Kept when the actor's account
    is deleted, with the address it had."""
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                              blank=True, related_name="+")
    actor_email = models.EmailField(blank=True)
    action = models.CharField(max_length=40, help_text='e.g. "role.grant", "user.delete"')
    target = models.CharField(max_length=200, blank=True, help_text="Who or what it was done to")
    detail = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.actor_email} {self.action} {self.target}"


def record(actor, action, target="", **detail):
    return AdminAction.objects.create(actor=actor, actor_email=getattr(actor, "username", ""),
                                      action=action, target=str(target)[:200], detail=detail)


class Broadcast(models.Model):
    """An email the admin sent to the team (staff/emails.py)."""
    subject = models.CharField(max_length=200)
    body = models.TextField()
    audience = models.CharField(max_length=40)
    recipients = models.PositiveIntegerField(default=0)
    failed = models.PositiveIntegerField(default=0)
    sent_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                blank=True, related_name="+")
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-sent_at"]

    def __str__(self):
        return self.subject


class ReviewAssignment(models.Model):
    """A book, or a range of its chapters, in one review layer that an
    editor has asked a reviewer to review, by a date or not
    (staff/assignments.py). Whether it is done is worked out from the
    layer's review states; closing it is the editor's."""
    layer = models.CharField(max_length=3, help_text="grc or hbo for the meaning, a reading language for wording")
    book = models.CharField(max_length=3)
    chapter_from = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Empty for the whole book")
    chapter_to = models.PositiveSmallIntegerField(null=True, blank=True)
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name="review_assignments")
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                    blank=True, related_name="+")
    due = models.DateField(null=True, blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["created_at", "id"]
        indexes = [models.Index(fields=["assignee", "closed_at"], name="review_assignment_open")]

    def __str__(self):
        return f"{self.layer} {self.book} {self.chapter_from or ''}-{self.chapter_to or ''} {self.assignee_id}"


def shown_actor(action, viewer, super_admin):
    """Who did action, as viewer may see it: the address for a super admin
    (who manages the team) or for viewer's own actions; otherwise the
    person's first name, so team addresses aren't handed to every role."""
    if super_admin or (action.actor_id and action.actor_id == viewer.id):
        return action.actor_email
    return (action.actor.first_name if action.actor else "") or "A team member"

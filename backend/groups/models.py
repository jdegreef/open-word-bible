"""Reading groups: a few readers following one reading plan together.

Members see each other's display names (never addresses), how far each has
read in the group's plan, if that member shares it, and what members write
about each day's reading. Nothing else of a member's is shown: notes,
highlights and bookmarks stay private. A group is joined with its invite
link; its leader (whoever made it, or the longest-standing member after
them) can rename it, make a new link, remove members and posts, and close
it. groups/views.py has the endpoints.
"""
from django.conf import settings
from django.db import models


class ReadingGroup(models.Model):
    name = models.CharField(max_length=80)
    # A plan of data/plans.json, or a member's own plan ("my-..."): then plan
    # holds a copy of it, {name, days}, so every member reads the same days
    # under the same id.
    plan_id = models.CharField(max_length=40)
    plan = models.JSONField(default=dict, blank=True)
    # The invite link's code, which any member can copy again; a new one
    # (the leader's) stops the old link working.
    invite_code = models.CharField(max_length=32, unique=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Membership(models.Model):
    group = models.ForeignKey(ReadingGroup, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="group_memberships")
    leader = models.BooleanField(default=False)
    share_progress = models.BooleanField(default=True, help_text="Whether the others see how far they have read")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["group", "user"], name="unique_membership")]
        ordering = ["joined_at", "id"]

    def __str__(self):
        return f"{self.user} in {self.group}"


class GroupPost(models.Model):
    """What a member wrote about one day of the group's plan."""
    group = models.ForeignKey(ReadingGroup, on_delete=models.CASCADE, related_name="posts")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="group_posts")
    day = models.PositiveSmallIntegerField()
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["created_at", "id"]

    def __str__(self):
        return f"Day {self.day} in {self.group}"

"""Reading groups (groups/models.py). Every endpoint needs an account, and
a display name to be known by in a group.

GET    /api/groups                         the reader's groups
POST   /api/groups  {name, plan_id, plan}  start one, as its leader
GET    /api/groups/invite/<code>           what an invite link is for
POST   /api/groups/join  {code}            join with it
GET    /api/groups/<id>                    a group: members, their progress, posts
PATCH  /api/groups/<id>  {name} (leader), {share_progress} (anyone)
DELETE /api/groups/<id>                    close it (leader)
POST   /api/groups/<id>/leave
POST   /api/groups/<id>/invite             a new link; the old one stops (leader)
DELETE /api/groups/<id>/members/<id>       remove a member (leader)
POST   /api/groups/<id>/posts {day, text}  write about a day of the plan
DELETE /api/groups/<id>/posts/<id>         delete a post (its writer, or the leader)
"""
import secrets
from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts import reading
from accounts.models import ReaderState
from accounts.reminders import built_in_plans

from .models import GroupPost, Membership, ReadingGroup

MAX_GROUPS = 20          # a reader's groups
MAX_MEMBERS = 50
MAX_POST = 2000
POSTS_PER_HOUR = 30
POSTS_SHOWN = 500


def _error(detail, code, http_status=status.HTTP_400_BAD_REQUEST):
    return Response({"detail": detail, "code": code}, status=http_status)


NOT_FOUND = ("No such group, or you are not in it.", "not_found", status.HTTP_404_NOT_FOUND)
NEED_NAME = ("Choose a display name on your account page first: it is how the group knows you.", "need_name",
             status.HTTP_409_CONFLICT)
LEADER_ONLY = ("Only the group's leader can do that.", "forbidden", status.HTTP_403_FORBIDDEN)


def _data(request):
    return request.data if isinstance(request.data, dict) else {}


def _name(value):
    name = " ".join(str(value or "").split())
    if not name or len(name) > 80:
        raise ValidationError({"name": "Give the group a name, under 80 characters.", "code": "invalid_name"})
    return name


def _code():
    return secrets.token_urlsafe(12)


def _plan(data):
    """(plan_id, plan) for a new group: a plan of data/plans.json, or a copy
    of one of the reader's own."""
    pid = str(data.get("plan_id") or "")
    if pid in built_in_plans():
        return pid, {}
    if pid.startswith("my-"):
        try:
            plan = reading._myplans({pid: {**(data.get("plan") or {}), "at": 0}})[pid]
        except (reading.Invalid, TypeError):
            plan = None
        if plan and plan.get("days"):
            return pid, {"name": plan["name"], "days": plan["days"]}
    raise ValidationError({"plan_id": "Choose a reading plan.", "code": "invalid_plan"})


def _plan_name(g, lang="en"):
    if g.plan:
        return g.plan.get("name", "")
    plan = built_in_plans().get(g.plan_id) or {}
    names = plan.get("name") or {}
    return names.get(lang) or names.get("en", g.plan_id)


def _days(g):
    plan = g.plan if g.plan else built_in_plans().get(g.plan_id) or {}
    return len(plan.get("days") or [])


def _membership(request, group_id):
    return (Membership.objects.select_related("group").filter(group_id=group_id, user=request.user).first())


def summary(m, lang="en"):
    g = m.group
    return {"id": g.id, "name": g.name, "plan_id": g.plan_id, "plan_name": _plan_name(g, lang), "days": _days(g),
            "members": g.members.count(), "leader": m.leader}


def detail(m, lang="en"):
    g = m.group
    members = list(g.members.select_related("user"))
    states = {s.user_id: s for s in ReaderState.objects.filter(user__in=[x.user for x in members])}
    out_members = []
    for x in members:
        progress = None
        if x.share_progress or x.user_id == m.user_id:
            plans = (states.get(x.user_id).plans or {}) if x.user_id in states else {}
            rec = (plans.get("plans") or {}).get(g.plan_id)
            progress = {"done": rec.get("done", []), "start": rec.get("start")} if rec else {"done": [], "start": None}
        out_members.append({"id": x.id, "name": x.user.first_name, "leader": x.leader, "me": x.user_id == m.user_id,
                            "share_progress": x.share_progress, "progress": progress})
    posts = list(g.posts.select_related("user").order_by("-created_at", "-id")[:POSTS_SHOWN])[::-1]
    return {**summary(m, lang), "plan": g.plan or None, "invite": g.invite_code, "share_progress": m.share_progress,
            "member_list": out_members,
            "posts": [{"id": p.id, "day": p.day, "text": p.text, "name": p.user.first_name,
                       "mine": p.user_id == m.user_id, "created_at": p.created_at,
                       "can_delete": m.leader or p.user_id == m.user_id} for p in posts]}


def _lang(request):
    lang = request.GET.get("lang", "en")
    return lang if isinstance(lang, str) else "en"


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def groups(request):
    user = request.user
    if request.method == "GET":
        return Response([summary(m, _lang(request)) for m in
                         Membership.objects.filter(user=user).select_related("group").order_by("-group__created_at")])
    if not user.first_name.strip():
        return _error(*NEED_NAME)
    data = _data(request)
    name = _name(data.get("name"))
    pid, plan = _plan(data)
    if Membership.objects.filter(user=user).count() >= MAX_GROUPS:
        return _error(f"You can be in up to {MAX_GROUPS} groups.", "too_many")
    with transaction.atomic():
        g = ReadingGroup.objects.create(name=name, plan_id=pid, plan=plan, invite_code=_code(), created_by=user)
        m = Membership.objects.create(group=g, user=user, leader=True)
    return Response(detail(m, _lang(request)), status=status.HTTP_201_CREATED)


def _by_code(code):
    return ReadingGroup.objects.filter(invite_code=str(code or "")).first() if code else None


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def invite(request, code):
    g = _by_code(code)
    if g is None:
        return _error("This invite link doesn't work any more. Ask the group for a new one.", "bad_invite",
                      status.HTTP_404_NOT_FOUND)
    mine = g.members.filter(user=request.user).first()
    return Response({"name": g.name, "plan_name": _plan_name(g, _lang(request)), "days": _days(g),
                     "members": g.members.count(), "member": mine.group_id if mine else None})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def join(request):
    user = request.user
    with transaction.atomic():
        g = _by_code(_data(request).get("code"))
        if g is not None:
            g = ReadingGroup.objects.select_for_update().get(pk=g.pk)
        if g is None:
            return _error("This invite link doesn't work any more. Ask the group for a new one.", "bad_invite",
                          status.HTTP_404_NOT_FOUND)
        m = g.members.filter(user=user).first()
        if m is None:
            if not user.first_name.strip():
                return _error(*NEED_NAME)
            if g.members.count() >= MAX_MEMBERS:
                return _error(f"This group is full ({MAX_MEMBERS} members).", "full", status.HTTP_409_CONFLICT)
            if Membership.objects.filter(user=user).count() >= MAX_GROUPS:
                return _error(f"You can be in up to {MAX_GROUPS} groups.", "too_many")
            m = Membership.objects.create(group=g, user=user)
    return Response(detail(m, _lang(request)))


@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def group(request, group_id):
    m = _membership(request, group_id)
    if m is None:
        return _error(*NOT_FOUND)
    if request.method == "DELETE":
        if not m.leader:
            return _error(*LEADER_ONLY)
        m.group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    if request.method == "PATCH":
        data = _data(request)
        if "name" in data:
            if not m.leader:
                return _error(*LEADER_ONLY)
            m.group.name = _name(data["name"])
            m.group.save(update_fields=["name"])
        if "share_progress" in data:
            if not isinstance(data["share_progress"], bool):
                raise ValidationError({"share_progress": "Send true or false."})
            m.share_progress = data["share_progress"]
            m.save(update_fields=["share_progress"])
    return Response(detail(m, _lang(request)))


def _leave(m):
    """Take m out; a group without its leader passes to its longest-standing
    member, and one with nobody left is closed."""
    g = m.group
    with transaction.atomic():
        m.delete()
        rest = g.members.order_by("joined_at", "id")
        if not rest.exists():
            g.delete()
        elif not rest.filter(leader=True).exists():
            rest.filter(pk=rest.first().pk).update(leader=True)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def leave(request, group_id):
    m = _membership(request, group_id)
    if m is None:
        return _error(*NOT_FOUND)
    _leave(m)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def new_invite(request, group_id):
    m = _membership(request, group_id)
    if m is None:
        return _error(*NOT_FOUND)
    if not m.leader:
        return _error(*LEADER_ONLY)
    m.group.invite_code = _code()
    m.group.save(update_fields=["invite_code"])
    return Response(detail(m, _lang(request)))


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def member(request, group_id, member_id):
    m = _membership(request, group_id)
    if m is None:
        return _error(*NOT_FOUND)
    other = m.group.members.filter(id=member_id).first()
    if other is None:
        return _error("No such member.", "not_found", status.HTTP_404_NOT_FOUND)
    if other.id != m.id and not m.leader:
        return _error(*LEADER_ONLY)
    _leave(other)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def posts(request, group_id):
    m = _membership(request, group_id)
    if m is None:
        return _error(*NOT_FOUND)
    data = _data(request)
    text = str(data.get("text") or "").strip()
    day = data.get("day")
    if not text or len(text) > MAX_POST:
        raise ValidationError({"text": f"Write something, under {MAX_POST:,} characters.", "code": "invalid_text"})
    if not isinstance(day, int) or isinstance(day, bool) or not 0 < day <= max(_days(m.group), 1):
        raise ValidationError({"day": "Choose a day of the plan.", "code": "invalid_day"})
    hour_ago = timezone.now() - timedelta(hours=1)
    if GroupPost.objects.filter(user=request.user, created_at__gte=hour_ago).count() >= POSTS_PER_HOUR:
        return _error("You've written a lot this hour. Try again later.", "rate_limited",
                      status.HTTP_429_TOO_MANY_REQUESTS)
    GroupPost.objects.create(group=m.group, user=request.user, day=day, text=text)
    return Response(detail(m, _lang(request)), status=status.HTTP_201_CREATED)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def post(request, group_id, post_id):
    m = _membership(request, group_id)
    if m is None:
        return _error(*NOT_FOUND)
    p = m.group.posts.filter(id=post_id).first()
    if p is None:
        return _error("No such post.", "not_found", status.HTTP_404_NOT_FOUND)
    if p.user_id != request.user.id and not m.leader:
        return _error(*LEADER_ONLY)
    p.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

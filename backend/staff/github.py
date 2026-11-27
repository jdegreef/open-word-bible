"""GitHub's REST API for the repository the admin files issues in
(settings.OWB_GITHUB_REPO): drafting jobs, fix requests and article jobs,
and the work listed from them.

    call(path, method="GET", body=None, stop=None)

Every staff module reaches GitHub through call, and tests replace it there.
"""
import http.client
import json
import logging
import re
import urllib.request

from django.conf import settings
from django.core.cache import cache

from . import kept

log = logging.getLogger(__name__)


class GitHubError(Exception):
    pass


# A list read follows GitHub's pages (100 to a page) up to this many, so
# more than 100 open jobs are all seen (the duplicate check and "stalled"
# depend on it) without a runaway list holding up a request.
MAX_PAGES = 10
NEXT = re.compile(r'<([^>]+)>;\s*rel="next"')


def call(path, method="GET", body=None, stop=None):
    """GitHub's answer for path under the repository. A list is read page
    by page while there is a next page, up to MAX_PAGES, and until
    stop(page) is true for a page. Raises GitHubError when GitHub can't be
    reached or answers with an error."""
    url = f"https://api.github.com/repos/{settings.OWB_GITHUB_REPO}/{path}"
    data, url = _request(url, method, body)
    if not isinstance(data, list):
        return data
    pages = 1
    while url and pages < MAX_PAGES and not (stop and stop(data)):
        more, url = _request(url, "GET", None)
        data += more
        pages += 1
    return data


def _request(url, method, body):
    """(the JSON answer, the next page's URL or None)."""
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "open-word-bible-admin",
               "X-GitHub-Api-Version": "2022-11-28"}
    if settings.OWB_GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {settings.OWB_GITHUB_TOKEN}"
    data = json.dumps(body).encode() if body is not None else None
    if data:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            link = NEXT.search(r.headers.get("Link") or "")
            answer = json.load(r)
    # OSError covers URLError, timeouts and a dropped connection mid-read;
    # HTTPException a truncated answer (IncompleteRead, RemoteDisconnected).
    except (OSError, http.client.HTTPException, ValueError) as e:
        log.warning("GitHub %s %s failed: %s", method, url.split("?")[0], e)
        raise GitHubError from e
    if method != "GET":
        # An issue filed or changed: the rail's counts (staff/attention.py) ask again.
        cache.delete("staff.attention.github")
        kept.forget_lists()   # the open lists the admin keeps
    return answer, link[1] if link else None

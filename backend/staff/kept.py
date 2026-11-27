"""Answers read from GitHub, kept so a page doesn't wait on it.

    kept(key, fetch, fresh)   fetch()'s answer: a copy younger than fresh
                              seconds as it is; an older one (kept up to a
                              day) at once while a thread reads GitHub
                              again; with no copy, read now

GitHub takes from a fraction of a second to ten seconds a request, and a
list can be several pages. The open drafting jobs, fix requests and
article jobs, and CI's state on main, are read this way; github.call
forgets the lists when it files or changes an issue, so the next page reads
them again. (Work in progress keeps its own, with when it was read:
staff/work.py.)
"""
import threading
import time

from django.core.cache import cache
from django.db import connections

KEEP = 86400
LISTS = ("staff.kept.jobs", "staff.kept.fixes", "staff.kept.articles")


def kept(key, fetch, fresh):
    entry = cache.get(key)
    if entry is None:
        return _read(key, fetch)
    if time.time() - entry["at"] > fresh and cache.add(key + ".refreshing", 1, 300):
        threading.Thread(target=_read_quietly, args=(key, fetch), daemon=True).start()
    return entry["value"]


def forget_lists():
    cache.delete_many(list(LISTS))


def _read(key, fetch):
    value = fetch()
    cache.set(key, {"at": time.time(), "value": value}, KEEP)
    return value


def _read_quietly(key, fetch):
    try:
        _read(key, fetch)
    except Exception:   # noqa: BLE001 -- the kept copy stays; the next page asks again
        pass
    finally:
        cache.delete(key + ".refreshing")
        connections.close_all()   # this thread's own database connection

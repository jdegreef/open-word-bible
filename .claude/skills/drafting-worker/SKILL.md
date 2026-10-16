---
name: drafting-worker
description: Work one drafting job from the admin's queue: a GitHub issue labelled drafting-job, filed from openwordbible.org/admin/#jobs, asking for a book to be drafted in some languages. Use when asked to "work the drafting queue", "take a drafting job", or handle a drafting-job issue. One job per run, end to end.
---

# Work a drafting job

The admin's Drafting jobs page (`backend/staff/jobs.py`) files a GitHub issue
labelled `drafting-job` for each request. Its body names the book and the
languages, and ends with a machine-readable line:

    <!-- drafting-job {"book": "EZK", "languages": ["en"]} -->

## 1. Take one job

Use the GitHub MCP tools on `jdegreef/open-word-bible`. List open issues with
the `drafting-job` label, oldest first. Skip any with an assignee or a comment
from another session saying it is taken. Comment on the one you take
("Taken by a Claude session on branch `<your branch>`"), so the next session
skips it.

## 2. Check the book is free

Run the `check-book-before-translating` skill for the book and every language
the job names. The admin refused languages already drafted when the job was
filed, but main and other sessions move on. If the work is done or in
progress elsewhere, comment on the issue saying where, and stop.

## 3. Draft

Follow CLAUDE.md and the language's style brief (`docs/<language>-style.md`;
`docs/english-style.md` for English). English comes first: the admin will not
file a job for another language until the book is drafted in English.

- Every record is `ai_draft`. Nothing is marked reviewed by Claude.
- Never type Greek or Hebrew; load it from the pinned sources.
- One pull request per book and language, as `scripts/check.sh` passes.

## 4. Close the loop

Link each pull request to the issue ("Part of #N"). When every language the
job names is in a pull request, comment with the links. Close the issue once
the pull requests are merged (or leave that to the user if they merge them).

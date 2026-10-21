---
name: article-worker
description: Work one article job from the admin's queue: a GitHub issue labelled article-job, filed from openwordbible.org/admin/#articles, asking for articles to be translated into one language or brought up to date with their English. Use when asked to "work the article queue", "take an article job", or handle an article-job issue. One job per run, end to end.
---

# Work an article job

The admin's Articles page (`backend/staff/articles.py`) files a GitHub issue
labelled `article-job` for a language and a list of articles. Each line says
what to do with one article: translate it (missing), bring it up to date with
its English (out of date), or check it against the English and stamp it (not
stamped). It ends with a machine-readable line:

    <!-- article-job {"language": "fr", "slugs": ["the-niv", "the-kjv"]} -->

## 1. Take one job

Use the GitHub MCP tools on `jdegreef/open-word-bible`. List open issues with
the `article-job` label, oldest first. Skip any with an assignee or a comment
from another session saying it is taken. Comment on the one you take
("Taken by a Claude session on branch `<your branch>`").

## 2. Check it is still needed

Merge `origin/main` first, then run
`python3 scripts/check_translations.py --lang <code>`. Drop any article the
report no longer lists, and any another open pull request already covers.

## 3. Translate

The English article is `articles/<slug>.md`; the translation is
`articles/<lang>/<slug>.md`. Follow the language's style brief
(`docs/<language>-style.md`) and the existing translations in that folder for
terms and tone.

- Keep the front matter's `date`, `order`, `section` and `part` as the
  English has them; translate `title`, `summary` and `nav_title`.
- Bible quotations come from Open Word Bible's own text in that language where
  it is drafted (the site's quote markup links them); never from a reference
  Bible.
- For an out-of-date translation, diff the English against the version the
  translation was made from (`git log -p articles/<slug>.md`) and carry over
  what changed rather than retranslating from scratch.
- Never type Greek or Hebrew; copy it from the English article.

Then stamp each one: `python3 scripts/check_translations.py --stamp
articles/<lang>/<slug>.md`, and run `python3 scripts/build_site.py` (or
`scripts/check.sh --fast`) so the site still builds.

## 4. Close the loop

Open one pull request for the job, with "Fixes #N" in its body and the
articles listed. A long job can be split over several pull requests; say on
the issue which articles each covers.

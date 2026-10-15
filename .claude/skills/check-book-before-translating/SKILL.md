---
name: check-book-before-translating
description: Run before starting to translate or draft any book (or chapter range) of the Open Word Bible in any language, including before handing a book to subagents. Checks main, the live site and GitHub (open pull requests and claude/* branches) so the book is not already done or being worked on in another session.
---

# Check a book before translating it

Several sessions draft in parallel. Mark was once drafted twice in Spanish and
Swahili because nobody checked. Before starting a book, or handing one to a
subagent, check that it is free in the languages you are about to draft.
Check every book in a multi-book job, not only the first.

## 1. Main

```bash
git fetch origin main
python3 .claude/skills/check-book-before-translating/coverage.py BOOK LANG [LANG ...]
```

This prints how many records in each file of `content/BOOK/` already have each
language on `origin/main`. Draft only what is missing.

## 2. The live site

Fetch `https://openwordbible.org/read/` (WebFetch) and look for the book under
each language you plan to draft; it lists what is published, built from
`main`. If it disagrees with step 1, the deploy may lag; trust `main`, but
mention the gap.

## 3. GitHub: work in progress

Use the GitHub MCP tools on `jdegreef/open-word-bible`:

- **Open pull requests**: `list_pull_requests` (state open), then for each one
  whose title or branch could touch the book, `pull_request_read` with
  `get_files` and look for `content/BOOK/`. Also `search_pull_requests` for the
  book's name ("Acts", "1 Corinthians", ...) and the language names.
- **Recently pushed branches** without a PR: `list_branches`, then for each
  `claude/*` branch other than your own:

  ```bash
  git fetch origin <branch>
  git diff --stat origin/main...origin/<branch> -- content/BOOK
  ```

  A branch counts only if its diff to `content/BOOK` adds the languages you
  plan to draft (look at the diff, not just the file names).
- **Closed-but-unmerged PRs** from the last few days, so you can tell
  abandoned work from work in progress.

## 4. Decide

- **Done on main**: do not draft it again. Tell the user and move on to the
  next book.
- **In an open PR or a recent branch**: stop and ask the user, naming the PR
  or branch, its date and what it covers. Do not draft the same book and
  language in parallel.
- **Free**: claim it. Push your branch with the first finished chapter early
  and open a draft pull request titled with the book and languages (when the
  user has asked for PRs), so the next session's check finds it.

Report what you checked, in one or two lines, before you start drafting.

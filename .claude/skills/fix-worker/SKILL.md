---
name: fix-worker
description: Work one fix request from the admin's queue: a GitHub issue labelled fix-request, filed from openwordbible.org/admin (the verse inspector or the reader inbox), asking for a sentence's wording to change in one language. Use when asked to "work the fix queue", "take a fix request", or handle a fix-request issue. One request per run, end to end.
---

# Work a fix request

The admin's verse inspector and reader inbox (`backend/staff/fixes.py`) file a
GitHub issue labelled `fix-request` for each request. Its body names the
sentence, the file, the language, the levels, the wording now, the change asked
for and why, and sometimes the reader message that prompted it. It ends with a
machine-readable line:

    <!-- fix-request {"record": "JHN.1.1.s1", "verse": "JHN.1.1", "language": "fr", "levels": ["L", "B", "R"], "message": 12} -->

## 1. Take one request

Use the GitHub MCP tools on `jdegreef/open-word-bible`. List open issues with
the `fix-request` label, oldest first. Skip any with an assignee or a comment
from another session saying it is taken. Comment on the one you take
("Taken by a Claude session on branch `<your branch>`").

## 2. Weigh it: a request, not an order

Open the record in its file and read it whole: the source words, the literal
gloss, the meaning decisions and the language's rendering decisions. Then
judge the request against:

- the Greek or Hebrew (from the pinned source data; never typed by hand);
- the language's style brief (`docs/<language>-style.md`) and the settled key
  terms (`data/key_terms.json`): a request to change a key term is a change
  for every use, so say so on the issue and ask the founder rather than
  changing one verse;
- the three levels' aims (Literal follows the original closely; Balanced is
  accurate and natural; Readable is plain).

A change of **meaning** is a meaning decision, shared by every language: say
so on the issue and stop; don't change one language's wording to carry it.
A disagreement a reader setting already covers (`{{setting:a|b}}`) needs no
change.

## 3. Change it, or explain why not

If the request holds: edit the renderings at the levels it names, and update
or add the language's rendering decision (choice, alternatives, reason) so the
record says why the wording is what it is. Keep `"status": "ai_draft"`.
Alignments for that language and level must still fit the new wording.
Run `python3 -m owb.validate` on the file and `scripts/check.sh --fast`, then
open one pull request for the request, titled with the verse and language,
with "Fixes #N" in its body.

If it doesn't hold: comment on the issue with the reasoning (what the source
says, what the brief says), and close it as not planned.

## 4. Close the loop

If the issue names a reader message, the editor answers the reader from the
admin inbox; put one line in your PR or closing comment that an editor can
pass on.

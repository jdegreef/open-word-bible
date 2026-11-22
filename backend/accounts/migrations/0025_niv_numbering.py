"""Move readers' verses saved before the site used NIV numbers
(2026-11-21) to the NIV's, as web/site.js moves the browser's copy
(owb/renumber.py): bookmarks, highlights and notes (Mark), passage notes,
verses being memorized and the reading place. Only what was saved before
the switch moves; two of ours that the NIV makes one verse are merged."""
from django.db import migrations

from owb import renumber


def _mark(row):
    entry = {"at": row.updated_at}
    for key, field in (("b", "bookmark"), ("h", "highlight"), ("n", "note"), ("t", "tags"),
                       ("text", "text"), ("lang", "lang")):
        if getattr(row, field):
            entry[key] = getattr(row, field)
    return entry


def _passage_note(row):
    entry = {"at": row.updated_at}
    for key, field in (("n", "note"), ("t", "tags"), ("text", "text"), ("lang", "lang")):
        if getattr(row, field):
            entry[key] = getattr(row, field)
    return entry


def _rows(model, field, to_entry, fields, by):
    """Move one model's rows, a reader at a time."""
    moving = [r for r in model.objects.filter(updated_at__lt=renumber.SWITCHED_MS).only("user_id", field)
              if by(getattr(r, field)) != getattr(r, field)]
    for user_id in sorted({r.user_id for r in moving}):
        rows = {getattr(r, field): r for r in model.objects.filter(user_id=user_id)}
        moved = renumber.store({k: to_entry(r) for k, r in rows.items()}, by)
        for key, row in rows.items():
            if key not in moved:
                row.delete()
        for key, entry in moved.items():
            row = rows.get(key) or model(user_id=user_id, **{field: key})
            values = {"note": entry.get("n", ""), "text": entry.get("text", ""), "lang": entry.get("lang", ""),
                      "tags": entry.get("t", []), "updated_at": entry["at"]}
            if "bookmark" in fields:
                values.update(bookmark=bool(entry.get("b")), highlight=entry.get("h", ""))
            if row.pk and all(getattr(row, k) == v for k, v in values.items()):
                continue
            for k, v in values.items():
                setattr(row, k, v)
            row.save()


def forwards(apps, schema_editor):
    _rows(apps.get_model("accounts", "Mark"), "verse", _mark, ["bookmark"], renumber.verse)
    _rows(apps.get_model("accounts", "PassageNote"), "passage", _passage_note, [], renumber.passage)
    for state in apps.get_model("accounts", "ReaderState").objects.exclude(memory={}):
        memory = renumber.store(state.memory, renumber.passage)
        if memory != state.memory:
            state.memory = memory
            state.save(update_fields=["memory"])
    for place in apps.get_model("accounts", "ReadingPlace").objects.filter(updated_at__lt=renumber.SWITCHED_MS):
        p = renumber.place({"book": place.book, "chapter": place.chapter, "verse": place.verse,
                            "at": place.updated_at})
        if (p["chapter"], p["verse"]) != (place.chapter, place.verse):
            place.chapter, place.verse = p["chapter"], p["verse"]
            place.save(update_fields=["chapter", "verse"])


class Migration(migrations.Migration):
    dependencies = [("accounts", "0024_system_accounts")]
    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]

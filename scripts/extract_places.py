"""Write data/places.json and data/basemap.json, the reader's maps (the
"Where it happens" map in the panel, web/map.js).

data/places.json gives each place in data/names.json a point and whether
its site is known, from OpenBible.info's Bible Geocoding Data (CC BY 4.0).
A place is matched to OpenBible's by the verses both say name it (moved to
English numbering, which OpenBible uses) and by a name OpenBible records
for it appearing in ours ("Antioch" in "Antioch in Syria"). A site is known
when OpenBible's best identification scores at least SURE out of 1000;
otherwise the map draws it as uncertain. Each place also carries that score
as its "confidence". Where no OpenBible place in a name's verses has one of
its names, a name inside OpenBible's ("Achor" in "Valley of Achor") or, as a
last resort, the one OpenBible place called exactly that, is used.

Words of the text that data/names.json has no card for yet are located too,
in "more": a proper noun (MACULA Hebrew's Np, a Greek lemma with a capital)
whose MACULA gloss is one of an OpenBible place's names, keyed
"strong|lemma|gloss", in the verses where OpenBible names that place (so a
man who shares a town's name is not put on the map). Where OpenBible names
two places so, the one it names in at least MORE_SHARE of those verses is
used, or none. A gloss MACULA splits word by word ("Ezion", "Geber") is
also tried whole. The reader gives such a word a place card
with its point until a named card is written. Only points are used: the
repository's geometry files include OpenStreetMap data under another
licence.

data/basemap.json is the land, lakes and rivers of the lands of the Bible,
from Natural Earth (public domain), cut to BOX and simplified.

The files are checked in so a deploy never needs the source clones.

Usage: OWB_VENDOR=<sources dir> python3 scripts/extract_places.py [--check]

--check exits non-zero if a file is missing or out of date.
"""
import argparse
import glob
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from owb import refs, versification  # noqa: E402
from owb.sources import LOCK, vendor_dir  # noqa: E402

PLACES = ROOT / "data" / "places.json"
BASEMAP = ROOT / "data" / "basemap.json"
GEOCODING = "openbible-geocoding"
NATURAL_EARTH = "natural-earth"
# OpenBible's identification score (out of 1000) from which a site is
# drawn as known: Capernaum (842) is, Cana (690) and Sychar (620) are not.
SURE = 800
# The lands of the Bible, Spain to the Indus (India, Esther 1:1), Asia
# Minor to Ethiopia: (west, south, east, north) in degrees.
BOX = (-10.0, 12.0, 72.0, 46.0)
# Simplification tolerance in degrees: about a kilometre for coasts.
TOLERANCE = {"land": 0.01, "lakes": 0.004, "rivers": 0.01}
# OpenBible's place types drawn as a label over an area, not as a dot.
AREAS = {"region", "river", "body of water", "valley", "wadi", "island"}
# Where OpenBible names more than one place so, the share of those verses
# the one it names most must have to be used.
MORE_SHARE = 0.5
# Words in our glosses that are not part of a place's name.
NOT_NAME = {"the", "of", "to", "in", "from", "at", "and", "toward", "into", "on", "by"}
# Natural Earth draws rivers down to small streams; keep the larger.
RIVER_RANK = 7


def owb_places():
    """{(strong, lemma, name): set of our verse ids} for every place sense in
    data/names.json, from the verses whose words carry its lemma (a sense
    with "verses" has those; one without has the rest)."""
    names = json.loads((ROOT / "data" / "names.json").read_text(encoding="utf-8"))["names"]
    wanted = {}
    for n in names:
        senses = [s for s in n["senses"] if s["kind"] == "place"]
        if senses:
            wanted[(n["strong"], n["lemma"])] = senses
    out = {}
    for lang, prefix in (("grc", "G"), ("hbo", "H")):
        for path in sorted(glob.glob(str(ROOT / "data" / lang / "*.json"))):
            for vid, words in json.loads(Path(path).read_text(encoding="utf-8"))["verses"].items():
                for w in words:
                    key = (prefix + (w.get("strong") or "").lstrip("0"), w["lemma"])
                    senses = wanted.get(key)
                    if not senses:
                        continue
                    sense = next((s for s in senses if vid in s.get("verses", [])), None) \
                        or next((s for s in senses if "verses" not in s), None)
                    if sense:
                        out.setdefault(key + (sense["name"],), set()).add(vid)
    return out


def proper_nouns():
    """{(strong, lemma): {"verses": {vid}, "gloss": {name: count}}} for the
    proper nouns of the text that data/names.json has no entry for: a
    Hebrew word MACULA marks Np, a Greek lemma that starts with a capital.
    A gloss's name is its capitalised words ("to.the.Gilgal" is Gilgal)."""
    names = json.loads((ROOT / "data" / "names.json").read_text(encoding="utf-8"))["names"]
    known = {(n["strong"], n["lemma"]) for n in names}
    out = {}
    for lang, prefix in (("grc", "G"), ("hbo", "H")):
        for path in sorted(glob.glob(str(ROOT / "data" / lang / "*.json"))):
            for vid, words in json.loads(Path(path).read_text(encoding="utf-8"))["verses"].items():
                for w in words:
                    proper = w["morph"].startswith("Np") if prefix == "H" else w["lemma"][:1].isupper()
                    key = (prefix + (w.get("strong") or "").lstrip("0"), w["lemma"])
                    # Not a word MACULA joins to another's number ("1886a|0725"),
                    # nor a one-letter prefix ("the") carrying a name's tag.
                    letters = [c for c in w["lemma"] if not unicodedata.combining(c)]
                    if not proper or key in known or "|" in key[0] or len(letters) < 2:
                        continue
                    name = " ".join(x for x in re.split(r"[.\s]+", re.sub(r"[\[\]()]", "", w.get("gloss") or ""))
                                    if x[:1].isupper() and x.lower() not in NOT_NAME)
                    # A people ("Gazites", "Timnite") is not a place.
                    if not name or name.endswith(("ite", "ites")):
                        continue
                    entry = out.setdefault(key, {"verses": set(), "gloss": {}, "parts": {}})
                    entry["verses"].add(vid)
                    entry["gloss"][name] = entry["gloss"].get(name, 0) + 1
                    entry["parts"].setdefault(vid, []).append(name)
    # A name MACULA glosses word by word ("Ezion", "Geber") is also tried whole.
    for entry in out.values():
        for parts in entry.pop("parts").values():
            whole = " ".join(dict.fromkeys(parts))
            if len(parts) > 1 and whole not in entry["gloss"]:
                entry["gloss"][whole] = 0
    return out


def english(vid):
    """Our verse id as English-numbered "BOOK C:V" (OpenBible's usx form)."""
    return {f"{r.book} {r.chapter}:{r.verse}" for r in versification.to_english(refs.parse(vid))}


def best_point(place):
    """(lon, lat, score) of an OpenBible place's best identification that
    has a point, or None."""
    for ident in place.get("identifications", []):
        score = (ident.get("score") or {}).get("time_total", 0)
        for res in ident.get("resolutions", []):
            if res.get("lonlat"):
                lon, lat = (float(x) for x in res["lonlat"].split(","))
                return lon, lat, score
    return None


def words(text):
    return re.findall(r"[a-z]+", text.lower())


def named(ours, theirs, inside=False):
    """How well one of OpenBible's names for a place matches ours: 2 if it
    opens our name ("Bethany" in "Bethany beyond the Jordan"), 1 if it is
    elsewhere in it ("Jordan"), 0 if none is. "the" is not a name. With
    inside, our name within one of theirs ("Achor" in "Valley of Achor")
    also counts 1."""
    mine = [w for w in words(ours) if w != "the"]
    best = 0
    for name in theirs:
        w = [x for x in words(name) if x != "the"]
        if w and mine[:len(w)] == w:
            return 2
        if w and any(mine[i:i + len(w)] == w for i in range(len(mine))):
            best = 1
        if inside and mine and any(w[i:i + len(mine)] == mine for i in range(len(w))):
            best = 1
    return best


def exactly(ours, place):
    """Whether one of OpenBible's names for a place is our name, word for word."""
    mine = [w for w in words(ours) if w != "the"]
    return any([x for x in words(n) if x != "the"] == mine for n in place.get("translation_name_counts", {}))


def located(place):
    """{"at", "sure", "area", "confidence"} for an OpenBible place, or None."""
    point = best_point(place)
    if not point:
        return None
    lon, lat, score = point
    types = set(place.get("types", []))
    return {"at": [round(lon, 3), round(lat, 3)], "sure": score >= SURE,
            "area": bool(types & AREAS) and "settlement" not in types, "confidence": score}


def by_verse(ob):
    """OpenBible's places by the verses that name them ("JOS 4:19")."""
    out = {}
    for p in ob:
        for v in p.get("verses", []):
            out.setdefault(v.get("usx"), []).append(p)
    return out


def match(places, ob):
    """{key: {"at", "sure", "area", "confidence"}} for our places OpenBible
    locates."""
    verses_of = by_verse(ob)
    out = {}
    for key, verses in sorted(places.items()):
        best = None
        for inside in (False, True):
            counts = {}
            for vid in verses:
                for usx in english(vid):
                    for p in verses_of.get(usx, []):
                        how = named(key[2], p.get("translation_name_counts", {}), inside)
                        if how:
                            n, _ = counts.get(p["id"], (0, how))
                            counts[p["id"]] = (n + 1, how)
            if counts:
                best = max(counts, key=lambda i: (counts[i][1], counts[i][0], i))
                break
        if best:
            place = next(p for p in ob if p["id"] == best)
        else:
            # Not in its verses (OpenBible reads them otherwise): the one
            # place OpenBible calls exactly this, if only one is.
            same = [p for p in ob if exactly(key[2], p)]
            if len(same) != 1:
                continue
            place = same[0]
        where = located(place)
        if where:
            out["|".join(key)] = where
    return out


def verse_order(vid):
    """A verse id's place in the Bible, for sorting."""
    r = refs.parse(vid)
    return (refs.BOOK_CODES.index(r.book), r.chapter, r.verse)


def match_more(nouns, ob):
    """{"strong|lemma|name": {"at", "sure", "area", "confidence", "verses"}}
    for the proper nouns data/names.json has no card for that OpenBible
    names, by their gloss, in the verses where it does."""
    verses_of = by_verse(ob)
    out = {}
    for (strong, lemma), entry in sorted(nouns.items()):
        # The commonest gloss OpenBible has a place for in the word's verses.
        for name in sorted(entry["gloss"], key=lambda g: (-entry["gloss"][g], g)):
            found = {}
            for vid in entry["verses"]:
                for usx in english(vid):
                    for p in verses_of.get(usx, []):
                        if exactly(name, p):
                            found.setdefault(p["id"], set()).add(vid)
            if found:
                break
        if not found:
            continue
        # Where OpenBible names two places so (the town and the wilderness
        # of Ziph), the one it names most, if that is most of them.
        best = max(found, key=lambda i: (len(found[i]), i))
        if len(found[best]) < MORE_SHARE * len(set().union(*found.values())):
            continue
        where = located(next(p for p in ob if p["id"] == best))
        if where:
            where["verses"] = sorted(found[best], key=verse_order)
            out[f"{strong}|{lemma}|{name}"] = where
    return out


def clip(ring, box, closed):
    """A ring or line cut to the box (Sutherland-Hodgman for rings; lines
    are split where they leave it)."""
    w, s, e, n = box
    if not closed:
        parts, cur = [], []
        for x, y in ring:
            if w <= x <= e and s <= y <= n:
                cur.append((x, y))
            elif cur:
                parts.append(cur)
                cur = []
        if cur:
            parts.append(cur)
        return parts
    edges = [(lambda p: p[0] >= w, lambda a, b: (w, a[1] + (b[1] - a[1]) * (w - a[0]) / (b[0] - a[0]))),
             (lambda p: p[0] <= e, lambda a, b: (e, a[1] + (b[1] - a[1]) * (e - a[0]) / (b[0] - a[0]))),
             (lambda p: p[1] >= s, lambda a, b: (a[0] + (b[0] - a[0]) * (s - a[1]) / (b[1] - a[1]), s)),
             (lambda p: p[1] <= n, lambda a, b: (a[0] + (b[0] - a[0]) * (n - a[1]) / (b[1] - a[1]), n))]
    pts = list(ring)
    for inside, cross in edges:
        if not pts:
            break
        out, prev = [], pts[-1]
        for cur in pts:
            if inside(cur):
                if not inside(prev):
                    out.append(cross(prev, cur))
                out.append(cur)
            elif inside(prev):
                out.append(cross(prev, cur))
            prev = cur
        pts = out
    return [pts] if len(pts) >= 3 else []


def simplify_ring(pts, tol):
    """A closed ring simplified: split at the point farthest from its start,
    since a line from a point to itself measures nothing."""
    x0, y0 = pts[0]
    k = max(range(len(pts)), key=lambda i: (pts[i][0] - x0) ** 2 + (pts[i][1] - y0) ** 2)
    if k == 0:
        return pts
    return simplify(pts[:k + 1], tol) + simplify(pts[k:] + [pts[0]], tol)[1:-1]


def simplify(pts, tol):
    """Douglas-Peucker, iteratively."""
    if len(pts) < 3:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        (ax, ay), (bx, by) = pts[a], pts[b]
        dx, dy = bx - ax, by - ay
        norm = (dx * dx + dy * dy) ** 0.5 or 1e-12
        far, at = 0.0, None
        for i in range(a + 1, b):
            x, y = pts[i]
            d = abs(dy * (x - ax) - dx * (y - ay)) / norm
            if d > far:
                far, at = d, i
        if at is not None and far > tol:
            keep[at] = True
            stack += [(a, at), (at, b)]
    return [p for p, k in zip(pts, keep) if k]


def geometries(path, kind):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    for f in data["features"]:
        if kind == "rivers" and (f["properties"].get("scalerank") or 99) > RIVER_RANK:
            continue
        g = f["geometry"]
        if not g:
            continue
        if g["type"] == "Polygon":
            yield from g["coordinates"][:1]
        elif g["type"] == "MultiPolygon":
            for poly in g["coordinates"]:
                yield poly[0]
        elif g["type"] == "LineString":
            yield g["coordinates"]
        elif g["type"] == "MultiLineString":
            yield from g["coordinates"]


def basemap():
    base = vendor_dir() / NATURAL_EARTH / "geojson"
    out = {}
    for kind, name in (("land", "ne_10m_land"), ("lakes", "ne_10m_lakes"),
                       ("rivers", "ne_10m_rivers_lake_centerlines")):
        shapes = []
        for line in geometries(base / f"{name}.geojson", kind):
            for part in clip([tuple(p[:2]) for p in line], BOX, kind != "rivers"):
                part = (simplify(part, TOLERANCE[kind]) if kind == "rivers"
                        else simplify_ring(part, TOLERANCE[kind]))
                if len(part) >= (2 if kind == "rivers" else 3):
                    # Flat [lon, lat, lon, lat, ...] to three decimals.
                    shapes.append([round(c, 3) for p in part for c in p])
        out[kind] = shapes
    return out


def source(name, path):
    lock = LOCK[name]
    return f"{path} in {lock['repo'].removeprefix('https://github.com/')} at {lock['commit']}"


def build():
    ob = [json.loads(line) for line in
          (vendor_dir() / GEOCODING / "data" / "ancient.jsonl").read_text(encoding="utf-8").splitlines() if line]
    places = {
        "description": "Where the places in data/names.json are, for the reader's maps: keyed "
                       "\"strong|lemma|name\", each a point [longitude, latitude], whether its site "
                       "is known, OpenBible's confidence in it (0 to 1000), and whether it is an area "
                       "(a region, river, sea or island: drawn as a label, not a dot). \"more\" locates "
                       "the same way the proper nouns data/names.json has no card for yet, keyed "
                       "\"strong|lemma|MACULA's gloss\", in the verses listed. Written by "
                       "scripts/extract_places.py.",
        "source": "OpenBible.info Bible Geocoding Data (CC BY 4.0), " + source(GEOCODING, "data/ancient.jsonl"),
        "places": match(owb_places(), ob),
        "more": match_more(proper_nouns(), ob)}
    shapes = basemap()
    base = {"description": "Land, lakes and rivers for the reader's maps, cut to the lands of the Bible "
                           "(box: west, south, east, north) and simplified; each shape is a flat list "
                           "of longitude, latitude pairs. Written by scripts/extract_places.py.",
            "source": "Natural Earth (public domain), 1:10m, " + source(NATURAL_EARTH, "geojson/"),
            "box": list(BOX), **shapes}
    return {PLACES: json.dumps(places, ensure_ascii=False, indent=1) + "\n",
            BASEMAP: json.dumps(base, ensure_ascii=False, separators=(",", ":")) + "\n"}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="exit non-zero if a file is out of date")
    args = ap.parse_args(argv)
    stale = []
    for path, text in build().items():
        if path.is_file() and path.read_text(encoding="utf-8") == text:
            continue
        if args.check:
            stale.append(path)
            continue
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")
    for path in stale:
        print(f"out of date: {path.relative_to(ROOT)} (run scripts/extract_places.py)", file=sys.stderr)
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())

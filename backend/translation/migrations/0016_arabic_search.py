from django.db import migrations

# Arabic search: the Arabic Snowball stemmer (Postgres 13 and later) with
# accents removed first, as 0012_indonesian_search does for Indonesian. The
# stemmer strips the article (ال), the attached prepositions and
# conjunctions (و، ف، ب، ل، ك) and the common suffixes (pronouns, plurals,
# the dual), so "والكلمة" finds "كلمة". Arabic fields are folded before they
# are indexed (search.ARABIC: no short vowels, one alef, one yeh), as
# queries are. translation/search.py CONFIGS maps "ar" to it.
CREATE = ("CREATE TEXT SEARCH CONFIGURATION owb_arabic (COPY = arabic);"
          "ALTER TEXT SEARCH CONFIGURATION owb_arabic"
          " ALTER MAPPING FOR hword, hword_part, word WITH unaccent, arabic_stem;")
DROP = "DROP TEXT SEARCH CONFIGURATION IF EXISTS owb_arabic;"


class Migration(migrations.Migration):

    dependencies = [
        ("translation", "0015_drafted_counts_and_indexes"),
    ]

    operations = [
        migrations.RunSQL(CREATE, DROP),
    ]

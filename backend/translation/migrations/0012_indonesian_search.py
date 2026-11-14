from django.db import migrations

# Indonesian search: the Indonesian Snowball stemmer (Postgres 12 and later)
# with accents removed first, as 0010_russian_search does for Russian. The
# stemmer strips the particles (-lah, -kah, -pun), the possessives (-ku,
# -mu, -nya) and the common prefixes and suffixes, so "dikasihi" finds
# "kasih" and "diselamatkan" "keselamatan" (but "mengasihi" stems to "asih":
# a nasal prefix that replaced the root's first letter is not undone).
# translation/search.py CONFIGS maps "id" to it.
CREATE = ("CREATE TEXT SEARCH CONFIGURATION owb_indonesian (COPY = indonesian);"
          "ALTER TEXT SEARCH CONFIGURATION owb_indonesian"
          " ALTER MAPPING FOR hword, hword_part, word WITH unaccent, indonesian_stem;")
DROP = "DROP TEXT SEARCH CONFIGURATION IF EXISTS owb_indonesian;"


class Migration(migrations.Migration):

    dependencies = [
        ("translation", "0011_japanese_search"),
    ]

    operations = [
        migrations.RunSQL(CREATE, DROP),
    ]

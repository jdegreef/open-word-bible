from django.db import migrations

# Portuguese search: the Portuguese stemmer with accents removed first, as
# 0003_search does for English, Spanish and French ("coracao" finds
# "coração"). translation/search.py CONFIGS maps "pt" to it.
CREATE = ("CREATE TEXT SEARCH CONFIGURATION owb_portuguese (COPY = portuguese);"
          "ALTER TEXT SEARCH CONFIGURATION owb_portuguese"
          " ALTER MAPPING FOR hword, hword_part, word WITH unaccent, portuguese_stem;")
DROP = "DROP TEXT SEARCH CONFIGURATION IF EXISTS owb_portuguese;"


class Migration(migrations.Migration):

    dependencies = [
        ("translation", "0008_review_digest_and_changes"),
    ]

    operations = [
        migrations.RunSQL(CREATE, DROP),
    ]

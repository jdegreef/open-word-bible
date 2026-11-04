from django.db import migrations

# Russian search: the Russian stemmer with accents removed first, as
# 0003_search does for English, Spanish and French (unaccent also folds
# "ё" into "е", so "еще" finds "ещё"). translation/search.py CONFIGS maps
# "ru" to it. Hindi has no Postgres stemmer and uses owb_simple.
CREATE = ("CREATE TEXT SEARCH CONFIGURATION owb_russian (COPY = russian);"
          "ALTER TEXT SEARCH CONFIGURATION owb_russian"
          " ALTER MAPPING FOR hword, hword_part, word WITH unaccent, russian_stem;")
DROP = "DROP TEXT SEARCH CONFIGURATION IF EXISTS owb_russian;"


class Migration(migrations.Migration):

    dependencies = [
        ("translation", "0009_portuguese_search"),
    ]

    operations = [
        migrations.RunSQL(CREATE, DROP),
    ]

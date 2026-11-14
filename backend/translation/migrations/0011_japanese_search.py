from django.db import migrations

# Japanese search (translation/search.py): Japanese is written without
# spaces, so entries in it are indexed by character bigrams, which
# search.ngrams() writes out with spaces between them before the vector is
# built. owb_cjk only has to lower-case what it is given, as "simple" does.
# It has no unaccent: the kana voicing marks (ガ against カ) are kept, as
# search.fold() keeps them. search.CONFIGS maps "ja" to it.
CREATE = "CREATE TEXT SEARCH CONFIGURATION owb_cjk (COPY = simple);"
DROP = "DROP TEXT SEARCH CONFIGURATION IF EXISTS owb_cjk;"


class Migration(migrations.Migration):

    dependencies = [
        ("translation", "0010_russian_search"),
    ]

    operations = [
        migrations.RunSQL(CREATE, DROP),
    ]

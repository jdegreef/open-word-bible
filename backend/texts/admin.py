from django.contrib import admin

from .models import Edition, Verse, Word


@admin.register(Edition)
class EditionAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "language", "kind", "licence", "imported_at"]
    list_filter = ["kind", "language"]
    readonly_fields = [f.name for f in Edition._meta.fields]


@admin.register(Verse)
class VerseAdmin(admin.ModelAdmin):
    list_display = ["edition", "book", "chapter", "verse", "text"]
    list_filter = ["edition", "book"]
    search_fields = ["text"]
    readonly_fields = ["edition", "book", "chapter", "verse", "text"]
    list_select_related = ["edition"]
    show_full_result_count = False


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ["id", "book", "chapter", "verse", "text", "lemma", "morph", "gloss"]
    list_filter = ["edition", "lang"]
    search_fields = ["=id", "lemma", "gloss", "strong"]
    readonly_fields = [f.name for f in Word._meta.fields]
    show_full_result_count = False

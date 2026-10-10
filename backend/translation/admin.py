from django.contrib import admin

from .models import Decision, Rendering, ReviewEvent, Sentence


class RenderingInline(admin.TabularInline):
    model = Rendering
    extra = 0


class DecisionInline(admin.StackedInline):
    model = Decision
    extra = 0
    fields = [("key", "layer", "language", "levels", "category"), "tokens", "choice",
              "alternatives", "reason", ("uncertain", "footnote")]


class ReviewEventInline(admin.TabularInline):
    model = ReviewEvent
    extra = 0
    readonly_fields = ["created_at"]


@admin.register(Sentence)
class SentenceAdmin(admin.ModelAdmin):
    list_display = ["record_id", "status", "verse_range", "literal_gloss", "updated_at"]
    list_filter = ["status", "book"]
    search_fields = ["record_id", "literal_gloss", "renderings__text"]
    readonly_fields = ["record_id", "book", "chapter", "verse", "number", "refs",
                       "source_edition", "source_text_id", "tokens", "source_text", "updated_at"]
    inlines = [RenderingInline, DecisionInline, ReviewEventInline]

    @admin.display(description="Verses")
    def verse_range(self, obj):
        return obj.refs[0] if len(obj.refs) == 1 else f"{obj.refs[0]}–{obj.refs[-1]}"

    def save_formset(self, request, form, formset, change):
        # A review event is always made by the person saving it.
        for event in formset.save(commit=False):
            if isinstance(event, ReviewEvent) and not event.user_id:
                event.user = request.user
            event.save()
        for obj in formset.deleted_objects:
            obj.delete()
        formset.save_m2m()


@admin.register(ReviewEvent)
class ReviewEventAdmin(admin.ModelAdmin):
    list_display = ["sentence", "action", "language", "user", "created_at"]
    list_filter = ["action", "language"]
    readonly_fields = ["created_at"]

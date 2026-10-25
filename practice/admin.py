from django.contrib import admin
from .models import Attempt, Explanation, KnowledgePoint, KnowledgeSnippet, Question

@admin.register(KnowledgePoint)
class KnowledgePointAdmin(admin.ModelAdmin):
    list_display = ("code", "title")

@admin.register(KnowledgeSnippet)
class KnowledgeSnippetAdmin(admin.ModelAdmin):
    list_display = ("title", "point", "source_version", "published")
    list_filter = ("point", "published")

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("code", "point", "published")
    list_filter = ("point", "published")

@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "question", "is_correct", "created_at")
    readonly_fields = ("user", "question", "selected", "answer_snapshot",
                       "reference_snapshot", "is_correct", "created_at")
    def has_add_permission(self, request):
        return False

@admin.register(Explanation)
class ExplanationAdmin(admin.ModelAdmin):
    list_display = ("attempt", "mode", "model", "created_at")
    readonly_fields = ("attempt", "body", "mode", "model", "references",
                       "input_tokens", "output_tokens", "created_at")
    def has_add_permission(self, request):
        return False

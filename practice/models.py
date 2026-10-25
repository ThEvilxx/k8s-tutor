from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

class KnowledgePoint(models.Model):
    code = models.SlugField(unique=True)
    title = models.CharField(max_length=100)
    summary = models.TextField()
    def __str__(self):
        return self.title

class KnowledgeSnippet(models.Model):
    point = models.ForeignKey(KnowledgePoint, on_delete=models.CASCADE, related_name="snippets")
    title = models.CharField(max_length=120)
    content = models.TextField()
    source_url = models.URLField()
    source_version = models.CharField(max_length=40, default="Kubernetes v1.35")
    published = models.BooleanField(default=True)
    def __str__(self):
        return self.title

class Question(models.Model):
    code = models.SlugField(unique=True)
    point = models.ForeignKey(KnowledgePoint, on_delete=models.PROTECT, related_name="questions")
    stem = models.TextField()
    options = models.JSONField(help_text='例如 {"A": "选项一", "B": "选项二"}')
    answer = models.CharField(max_length=1)
    reference = models.TextField(help_text="教师维护的标准解析")
    published = models.BooleanField(default=True)
    def clean(self):
        if not isinstance(self.options, dict) or self.answer not in self.options:
            raise ValidationError("标准答案必须对应一个有效选项。")
        if any(k not in ("A", "B", "C", "D") for k in self.options):
            raise ValidationError("单选题选项仅支持 A、B、C、D。")
    def __str__(self):
        return self.stem[:60]

class Attempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="attempts")
    question = models.ForeignKey(Question, on_delete=models.PROTECT, related_name="attempts")
    selected = models.CharField(max_length=1)
    # 保留判分时的标准答案及解析快照，题库后续修改不覆盖历史。
    answer_snapshot = models.CharField(max_length=1)
    reference_snapshot = models.TextField()
    is_correct = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "is_correct"], name="attempt_user_correct")]
    def __str__(self):
        return f"{self.user_id} / {self.question.code}"

class Explanation(models.Model):
    attempt = models.OneToOneField(Attempt, on_delete=models.CASCADE, related_name="explanation")
    body = models.TextField()
    mode = models.CharField(max_length=20, choices=[
        ("mock", "演示讲解"), ("api", "模型生成"), ("fallback", "调用失败后标准解析")])
    model = models.CharField(max_length=100, blank=True)
    references = models.JSONField(default=list)
    input_tokens = models.PositiveIntegerField(default=0)
    output_tokens = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

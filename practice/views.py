from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import AnswerForm
from .models import Attempt, KnowledgePoint, Question
from .services import explain_attempt, submit_answer

@login_required
def home(request):
    questions = Question.objects.filter(published=True).select_related("point")
    point = request.GET.get("point", "")
    if point:
        questions = questions.filter(point__code=point)
    return render(request, "practice/home.html", {
        "questions": questions, "points": KnowledgePoint.objects.all(), "selected_point": point})

@login_required
def question(request, pk):
    item = get_object_or_404(Question, pk=pk, published=True)
    form = AnswerForm(request.POST or None, question=item)
    if request.method == "POST" and form.is_valid():
        attempt = submit_answer(user=request.user, question=item, selected=form.cleaned_data["selected"])
        return redirect("practice:attempt", pk=attempt.pk)
    return render(request, "practice/question.html", {"question": item, "form": form})

@login_required
def attempt(request, pk):
    record = get_object_or_404(
        Attempt.objects.select_related("question", "question__point"), pk=pk, user=request.user)
    return render(request, "practice/attempt.html", {"attempt": record})

@login_required
@require_POST
def explain(request, pk):
    record = get_object_or_404(
        Attempt.objects.select_related("question", "question__point"), pk=pk, user=request.user)
    explain_attempt(record)
    return redirect("practice:attempt", pk=record.pk)

@login_required
def mistakes(request):
    records = Attempt.objects.filter(user=request.user, is_correct=False).select_related("question")
    return render(request, "practice/mistakes.html", {"attempts": records})

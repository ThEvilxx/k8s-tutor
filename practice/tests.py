from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from .models import Attempt, Explanation, KnowledgeSnippet, Question
from .services import explain_attempt, retrieve_context, submit_answer

@override_settings(LLM_MODE="mock")
class PracticeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", verbosity=0)
        cls.user = get_user_model().objects.create_user("student", password="test-only-password")
        cls.other = get_user_model().objects.create_user("other", password="test-only-password")
        cls.question = Question.objects.get(code="pod-basic")
    def setUp(self):
        self.client.force_login(self.user)
    def record(self, selected="A"):
        return submit_answer(user=self.user, question=self.question, selected=selected)
    def test_seed_is_idempotent(self):
        call_command("seed_demo", verbosity=0)
        self.assertEqual(Question.objects.count(), 8)
    def test_correct_is_rule_based(self):
        self.assertTrue(self.record("B").is_correct)
    def test_wrong_answer_is_recorded(self):
        self.assertFalse(self.record("A").is_correct)
    def test_answer_snapshot_survives_question_change(self):
        record = self.record("B")
        self.question.answer = "A"
        self.question.reference = "变更后的解析"
        self.question.save()
        record.refresh_from_db()
        self.assertEqual(record.answer_snapshot, "B")
        self.assertTrue(record.is_correct)
        self.assertNotEqual(record.reference_snapshot, self.question.reference)
    def test_invalid_choice_creates_no_attempt(self):
        with self.assertRaises(ValueError):
            self.record("Z")
        self.assertFalse(Attempt.objects.exists())
    def test_question_rejects_bad_standard_answer(self):
        self.question.answer = "Z"
        with self.assertRaises(ValidationError):
            self.question.full_clean()
    def test_answer_page_does_not_reveal_reference(self):
        response = self.client.get(reverse("practice:question", args=[self.question.pk]))
        self.assertNotContains(response, self.question.reference)
    def test_student_cannot_read_other_attempt(self):
        record = submit_answer(user=self.other, question=self.question, selected="A")
        self.assertEqual(self.client.get(reverse("practice:attempt", args=[record.pk])).status_code, 404)
    def test_student_cannot_explain_other_attempt(self):
        record = submit_answer(user=self.other, question=self.question, selected="A")
        self.assertEqual(self.client.post(reverse("practice:explain", args=[record.pk])).status_code, 404)
    def test_mistakes_are_private(self):
        self.record()
        other = Question.objects.get(code="rollback")
        submit_answer(user=self.other, question=other, selected="A")
        response = self.client.get(reverse("practice:mistakes"))
        self.assertContains(response, self.question.stem)
        self.assertNotContains(response, other.stem)
    def test_mock_does_not_call_api(self):
        with patch("practice.services.call_model") as api:
            result = explain_attempt(self.record())
        api.assert_not_called()
        self.assertEqual(result.mode, "mock")
        self.assertIn("未调用大模型", result.body)
    def test_unpublished_snippets_are_not_retrieved(self):
        KnowledgeSnippet.objects.filter(point=self.question.point).update(published=False)
        self.assertEqual(retrieve_context(self.question), [])
    def test_explanation_is_reused(self):
        record = self.record()
        first = explain_attempt(record)
        self.assertEqual(first.pk, explain_attempt(record).pk)
        self.assertEqual(Explanation.objects.count(), 1)
    @override_settings(LLM_MODE="api")
    def test_api_failure_preserves_grade_and_falls_back(self):
        record = self.record()
        with patch("practice.services.call_model", side_effect=TimeoutError):
            result = explain_attempt(record)
        record.refresh_from_db()
        self.assertEqual(result.mode, "fallback")
        self.assertFalse(record.is_correct)
    @override_settings(LLM_MODE="api")
    def test_api_response_cannot_change_grade(self):
        record = self.record()
        with patch("practice.services.call_model", return_value=("模型错误声称回答正确", 100, 30)):
            result = explain_attempt(record)
        record.refresh_from_db()
        self.assertFalse(record.is_correct)
        self.assertEqual(result.input_tokens, 100)
    def test_explain_requires_post(self):
        self.assertEqual(self.client.get(reverse("practice:explain", args=[self.record().pk])).status_code, 405)
    def test_anonymous_redirects_to_login(self):
        self.client.logout()
        self.assertEqual(self.client.get("/").status_code, 302)
    def test_healthz_does_not_need_login(self):
        self.client.logout()
        self.assertEqual(self.client.get("/healthz/").json(), {"status": "ok"})
    def test_teacher_admin_requires_staff(self):
        self.assertEqual(self.client.get("/admin/").status_code, 302)
    def test_post_answer_creates_record(self):
        response = self.client.post(reverse("practice:question", args=[self.question.pk]), {"selected": "B"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Attempt.objects.get().is_correct)
    def test_template_escapes_model_html(self):
        record = self.record()
        Explanation.objects.create(attempt=record, body="<script>alert(1)</script>", mode="mock")
        response = self.client.get(reverse("practice:attempt", args=[record.pk]))
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, "<script>alert(1)</script>")

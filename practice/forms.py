from django import forms
class AnswerForm(forms.Form):
    selected = forms.ChoiceField(label="选择你的答案", widget=forms.RadioSelect)
    def __init__(self, *args, question, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["selected"].choices = list(question.options.items())

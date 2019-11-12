from django import forms
import uuid as UUID
from . import models

class AnswerForm(forms.Form):
    text = forms.Textarea()
    question = forms.UUIDField()
    author = forms.CharField(max_length=30)
    files = forms.TypedMultipleChoiceField(coerce=UUID.UUID)


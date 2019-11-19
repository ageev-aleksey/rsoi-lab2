from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class TagsList(forms.Field):
        def __init__(self, max_len_one_tag=30):
            super().__init__()
            self.max_len_one_tag = max_len_one_tag
        def to_python(self, value):
            if not value:
                return []
            return value

        def validate(self, value):
            """Check if value consists only of valid emails."""
            # Use the parent's handling of required fields, etc.
            for tag in value:
                if len(tag) > self.max_len_one_tag:
                    raise ValidationError(_("text length exceeds %(length)d character limit"),
                                          params = {"length": self.max_len_one_tag})



class Question(forms.Form):
    title = forms.CharField(max_length=100)
    text = forms.CharField()
    user = forms.CharField(max_length=30)
    tags = TagsList(max_len_one_tag=30)


class Answer(forms.Form):
    text = forms.CharField()
    user = forms.CharField(max_length=30)
    question = forms.UUIDField()

class Attach(forms.Form):
    file_name = forms.CharField(max_length=50)

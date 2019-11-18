from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import uuid as UUID

class ValuesList(forms.Field):
    def __init__(self, my_validator, *args, **kwargs):
        super().__init__(*args, **kwargs);
        self.my_validator = my_validator
    def to_python(self, value):
        if not value:
            return []
        return value

    def validate(self, value):
        """Check if value consists only of valid emails."""
        # Use the parent's handling of required fields, etc.
        for item in value:
            self.my_validator(item)
def text_len_validator(mex_text_len):
    def text_len(value):
        if len(value) > mex_text_len:
            raise ValidationError(_("text length exceeds %(length)d character limit"),
                                params={"length": mex_text_len})
    return text_len

def uuid_validator():
    def is_uuid(value):
        try:
            UUID.UUID(value)
        except:
            raise ValidationError(_("string must have a uuid format"))
    return is_uuid

class Question(forms.Form):
    title = forms.CharField(max_length=50)
    text = forms.CharField()
    user = forms.CharField(max_length=30)
    tags = ValuesList(my_validator=text_len_validator(30), required=False)
    files = ValuesList(my_validator=uuid_validator(), required=False)


class Answer(forms.Form):
    text = forms.Textarea()
    question = forms.UUIDField()
    author = forms.CharField(max_length=30)

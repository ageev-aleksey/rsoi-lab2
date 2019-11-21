from django import forms
import uuid as UUID
from . import models


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

def uuid_validator():
    def is_uuid(value):
        try:
            UUID.UUID(value)
        except:
            raise ValidationError(_("string must have a uuid format"))
    return is_uuid

class uuid_list(forms.Form):
    uuid= ValuesList(my_validator=uuid_validator())


class AnswerForm(forms.Form):
    text = forms.CharField()
    question = forms.UUIDField()
    user = forms.CharField(max_length=30)
    files = forms.TypedMultipleChoiceField(coerce=UUID.UUID)





class AttachFile(forms.Form):
    answer = forms.UUIDField()
    file = forms.UUIDField()

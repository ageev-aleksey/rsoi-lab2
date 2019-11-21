from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import uuid as UUID

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

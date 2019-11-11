from django import forms
from django.forms import ModelForm
from . import models

class UploadFileForms(ModelForm):
    class Meta:
        model = models.FileInfo
        fields = ["file_name", "user"]
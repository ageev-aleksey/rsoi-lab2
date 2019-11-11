from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import FileResponse
from . import models
import json
import hashlib
from . import forms
# Create your views here.

@csrf_exempt
def file_form_upload(request):
    if request.method == 'POST':
        form = forms.UploadFileForms(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect('/success/url/')
    else:
            f = forms.UploadFileForms()
            return render(request, 'form.html', context={'form': f.as_table()})


def handle_uploaded_file(f):
    import os
    print(os.getcwd())
    with open('./uploads/' + str(f), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)



@csrf_exempt
def file_add(request):
    """
    {
            "file_name": "test",
            "file_type": "jpg",
            "user": "ce292f20-b257-4c51-9342-226637bc998a"
        }"""
    if request.method == "POST":
        file_form = forms.UploadFileForms(json.loads(request.POST['info']))
        if file_form.is_valid():
            file_info = models.FileInfo()
            file_info.from_data(file_form.cleaned_data, request.FILES['file'])
            file_info.save()

    return HttpResponse("ok")


def get_file(request, file_name):
    print(file_name)
    return FileResponse(open("./uploads/" + file_name, 'rb'))
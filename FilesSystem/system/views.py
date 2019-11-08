from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from . import forms
# Create your views here.

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
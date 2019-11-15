from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import FileResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_GET
from . import models
import json
import logging
import uuid as UUID
import hashlib
from . import forms
# Create your views here.


class JsonResponseMethodNotAllowed(JsonResponse):
    status_code = 405
    def __init__(self, permitted_methods, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self['Allow'] = ', '.join(permitted_methods)

class JsonResponseNotFound(JsonResponse):
    status_code = 404

class JsonResponseBadRequest(JsonResponse):
    status_code = 400

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
            "user": "<user_name>"
    }"""
    if request.method == "POST":
        file_form = forms.UploadFileForms(json.loads(request.POST['info']))
        if file_form.is_valid():
            file_info = models.FileInfo()
            file_info.from_data(file_form.cleaned_data, request.FILES['file'])
            file_info.save()

    return JsonResponse({"type": "ok", "uuid": str(file_info.uuid)})


def file_work(request, file_uuid):
    if request.method == "GET":
        return get_file(request, file_uuid)
    elif request.method == "DELETE":
        return delete_file(request, file_uuid)

def get_file(request, file_uuid):
    try:
        file_info = models.FileInfo.objects.get(uuid=file_uuid)
    except ObjectDoesNotExist:
        return JsonResponseNotFound({"type": "error", "data": "file with uuid not exists"})
    return FileResponse(file_info.file.file)

def get_file_info(request, file_uuid):
    try:
        file_info = models.FileInfo.objects.get(uuid=file_uuid)
    except ObjectDoesNotExist:
        return JsonResponseNotFound({"type": "error", "data": "file with uuid not exists"})
    return JsonResponse(file_info.to_dict())

def delete_file(request, file_uuid):
    try:
        file_info = models.FileInfo.objects.get(uuid=file_uuid)
    except ObjectDoesNotExist:
        return JsonResponseNotFound({"type": "error", "data": "file with uuid not exists"})
    file_info.delete()
    return JsonResponse({})

@require_GET
def get_list_of_files_info(request):
    log = logging.getLogger("FileSystem.get_list_of_files_info")
    log.setLevel(logging.DEBUG)
    try:
        data = json.loads(request.body)
    except ValueError:
        return JsonResponseBadRequest({"type": "error", "data": "body of request must have containing a json object"})

    try:
        uuid_list = []
        for l in data["uuid"]:
            u = []
            for fuuid in l:
                print("++++++++++++")
                print(fuuid)
                print("++++++++++++")
                u.append(UUID.UUID(fuuid))
            uuid_list.append(u)
    except ValueError:
        return JsonResponseBadRequest({"type": "error", "data": "filed 'uuid' must be containing string of uuid type"})

    files_info = []
    for l in uuid_list:
        fi = []
        for fu in l:
            try:
                fi.append(models.FileInfo.objects.get(uuid=fu).to_dict())
            except:
                print("not found file from uuid: " + str(fu))
        files_info.append(fi)
    return JsonResponse({"type": "files_info_list", "files_info": files_info})

#todo убрать поле юзер в FileInfo, так как не используется авторизация
#todo убрать поле name в FileContainer, так как оно должно храниться в поле FileInfo
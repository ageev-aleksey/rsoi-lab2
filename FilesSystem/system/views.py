from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import FileResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.core.paginator import Paginator
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


@require_GET
@csrf_exempt
def get_all_files(request):
    try:
        page = request.GET['page']
    except KeyError:
        page = 1
    p = Paginator(models.FileInfo.objects.all().order_by("date"), 10)
    finfo_list = []
    for info in p.object_list:
        finfo_list.append(info.to_dict())
    return JsonResponse({"type": "files_list", "files": finfo_list, "page": page, "pages": p.num_pages})


@csrf_exempt
@require_POST
def file_add(request):
    """
    {
            "file_name": "test",
            "file_type": "jpg",
            "user": "<user_name>"
    }"""
    file_form = forms.UploadFileForms(json.loads(request.POST['info']))
    if file_form.is_valid():
        file_info = models.FileInfo()
        file_info.from_data(file_form.cleaned_data, request.FILES['file'])
        file_info.save()
        return JsonResponse({"type": "ok", "uuid": str(file_info.uuid)})
    return JsonResponseBadRequest({"type": "error", "data": file_form.errors})

@require_http_methods(["GET", 'DELETE'])
@csrf_exempt
def file_work(request, file_uuid):
    if request.method == "GET":
        return get_file(request, file_uuid)
    elif request.method == "DELETE":
        return delete_file(request, file_uuid)


@require_GET
@csrf_exempt
def get_file(request, file_uuid):
    try:
        file_uuid = UUID.UUID(file_uuid)
    except ValueError:
        return JsonResponseBadRequest({"type": "error", "data": "incorrect uuid of file"})
    try:
        file_info = models.FileInfo.objects.get(uuid=file_uuid)
    except ObjectDoesNotExist:
        return JsonResponseNotFound({"type": "error", "data": "file with uuid not exists"})
    return FileResponse(file_info.file.file)

@require_GET
@csrf_exempt
def get_file_info(request, file_uuid):
    try:
        file_uuid = UUID.UUID(file_uuid)
    except ValueError:
        return JsonResponseBadRequest({"type": "error", "data": "incorrect uuid of file"})
    try:
        file_info = models.FileInfo.objects.get(uuid=file_uuid)
    except ObjectDoesNotExist:
        return JsonResponseNotFound({"type": "error", "data": "file with uuid not exists"})
    return JsonResponse(file_info.to_dict())

@require_http_methods(['DELETE'])
@csrf_exempt
def delete_file(request, file_uuid):
    try:
        file_uuid = UUID.UUID(file_uuid)
    except ValueError:
        return JsonResponseBadRequest({"type": "error", "data": "incorrect uuid of file"})
    try:
        file_info = models.FileInfo.objects.get(uuid=file_uuid)
        file_container = file_info.file
    except ObjectDoesNotExist:
        return JsonResponseNotFound({"type": "error", "data": "file with uuid not exists"})
    file_info.delete()
    info = models.FileInfo.objects.filter(file=file_container)
    if info.count() == 0:
        file_container.delete()
    return JsonResponse({"type": "ok"})


@require_GET
@csrf_exempt
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
                print(fuuid)
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
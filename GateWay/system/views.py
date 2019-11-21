from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.http import JsonResponse, HttpResponse, FileResponse, HttpRequest
from . import forms
import logging
import requests
import json
import uuid
from . import service_config
# Create your views here.
class JsonResponseBadRequest(JsonResponse):
    status_code = 400
class JsonResponseNotFound(JsonResponse):
    status_code = 404
class JsonResponseNoContent(JsonResponse):
    status_code = 203
class JsonResponseCreated(JsonResponse):
    status_code = 201
class JsonResponseServerError(JsonResponse):
    status_code = 500

def download_file(url, file_name = "temporary"):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(file_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    return file_name


def file_unpack(file):
    return {'file', file}
#data = None, params = None, files=None
def connect(service_path,method, timeout=5, **kwargs):
    log = logging.getLogger('GetWay.connect')
    log.setLevel(logging.DEBUG)
    if method == "POST":
        con =  requests.post
    elif method == "GET":
        con = requests.get
    elif method == "DELETE":
        con = requests.delete
    else:
        con = requests.option
    counter = 0
    while(counter != 2):
        try:
            #params=params, data=data, files=files
            r = con(service_path, timeout=timeout, **kwargs)
            break
        except requests.exceptions.Timeout as exp:
            log.exception("connection timeout")
            counter = counter+1
        except ConnectionError as exp:
            raise exp
    if counter == 2:
        raise ConnectionError("Request time out")
    return r

@csrf_exempt
@require_GET
def get_questions_page(request):
    log = logging.getLogger("GetWay.get_questions_page")
    log.setLevel(logging.DEBUG)
    try:
        page = int(request.GET['page'])
    except KeyError:
        return JsonResponseBadRequest({"type": "error", "data": "request don't have a query parameter 'get'"})
    except ValueError:
        return JsonResponseBadRequest({"type": "error", "data": "query parameter 'get' mast have type int"})
    try:
        rquestions = connect(service_config.question_system["questions_list"], "GET", params={"page": page})
    except (ConnectionError, ValueError):
        return JsonResponseServerError({"type": "error", "data": "Unable to get a list of questions"})
    if rquestions.status_code == 200:
        try:
            data = rquestions.json()
            uuid_list = {"questions": []}
            for el in data["questions"]:
                uuid_list["questions"].append(el['uuid'])
            rcount_answers = connect(service_config.answer_system["count_answers_question"],
                                     "GET", data=json.dumps(uuid_list))
            print(rcount_answers.status_code)
            if rcount_answers.status_code == 200:
                count = rcount_answers.json()['count']
                res = {"type": "questions_paginate", "page": page, "pages": data["pages"],
                       "questions": []}
                for q in range(len(data["questions"])):
                    res["questions"].append(data["questions"][q])
                    res["questions"][-1]["answers"] = count[q]
                return JsonResponse(res)




        except Exception as exp:
            log.exception("Error, get count answers of question. " + str(exp))
    elif rquestions.status_code == 203:
        return JsonResponseNotFound({"type": "ok", "data": "questions not found"})
    return JsonResponse({"type": "ok"})

@csrf_exempt
@require_http_methods(["GET", "DELETE"])
def question_worker(request, question_uuid):
    if request.method == "GET":
        return get_question(request, question_uuid)
    else:
        return delete_question(request, question_uuid)

def get_question(request, question_uuid):
    """Страница долджна содержать:
        * Описание вопроса:
            -Автор
            -Заголовок
            -ПОлный текст
            -Описание прикрепленных файлов:
                -название
                -тип
        * Список ответов:
            -Описание ответа:
                -Автор
                -Текст
                -Описание прикрепленных файлов:
                    -Название
                    -Тип
    """
    log = logging.getLogger("gateway.get_question")
    log.setLevel(logging.DEBUG)
    try:
       uuid.UUID(question_uuid)
    except ValueError:
        return JsonResponseBadRequest({"type": "error", "data": "for choose concrete answer you must using a uuid"})
    try:
        page = request.GET['page']
    except KeyError:
        page = 1

    try:
        rquestion = connect(service_config.question_system['question'] + f"{question_uuid}/", "GET")
        if rquestion.status_code == 200:
            qdata = rquestion.json()
        elif rquestion.status_code == 404:
            return JsonResponseNotFound({'type': "error", "data": "question with uuid not found"})
    except Exception as exp:
        return JsonResponseServerError({"type": "error", "data": "unable to get question page"})
    try:
        ranswer = connect(service_config.answer_system['answers_for_question'], "GET",
                          params={"page": page, "question": question_uuid})
        if ranswer.status_code == 200:
            ans_data = ranswer.json()
        else:
            raise Exception
    except Exception as exp:
        return JsonResponseServerError({"type": "error", "data": "unable to get answers for question"})

    # files/list post: {"uuid": [[<uuids list for question>][<uuids list of answers>]]}
    files_list = [qdata["files"]]
    for answer in ans_data['answers']:
        files_list.append(answer['files'])

    res_response = {"type": "question_page", "question": qdata, "answers": ans_data['answers'],
                    "page": ans_data["page"], "pages": ans_data["pages"]}

    try:
        file_data = None
        rfile = connect(service_config.file_system['list_of_files'] , "GET", data=json.dumps({"uuid": files_list}))
        if rfile.status_code == 200:
            file_data = rfile.json()["files_info"]
        else:
            log.error("File system return status code: " + rfile.status_code)
    except ConnectionError as exp:
        log.error("Error connection to files system")
    except Exception as exp:
        log.error("File system return failed data")

    if file_data != None:
        res_response['question']['files'] = file_data[0]
        for i in range(len(res_response['answers'])):
            res_response['answers'][i]['files'] = file_data[i+1]
    else:
        del res_response['question']['files']
        for ans in res_response['answers']:
            del ans["files"]

    return JsonResponse(res_response)

@csrf_exempt
@require_POST
def create_question(request):
    try:
        data = json.loads(request.body)
    except ValueError:
        return JsonResponseBadRequest({"error": "body of request must be containing a json object"})
    question_data = forms.Question(data)
    if question_data.is_valid():
        conn = connect(service_config.question_system['add_question'], "POST",
                       data=json.dumps(question_data.cleaned_data))
        try:
            quuid = json.loads(conn.content)["uuid"]
        except:
            return JsonResponseServerError({"type": "error", "data": "internal server error"})
        if conn.status_code == 201:
            return JsonResponse({"type": "ok", "uuid": quuid })
        else:
            return HttpResponse(conn.content, status=500)
    return JsonResponseBadRequest({"type": "error", "data": question_data.errors})

@csrf_exempt
@require_POST
def create_answer(request, question_uuid):
    try:
        data = json.loads(request.body)
    except:
        return JsonResponseBadRequest({"error": "body of request must be containing a json object"})
    data["question"] = question_uuid
    adata = forms.Answer(data)
    if adata.is_valid():
        try:
            adata.cleaned_data["question"] = str(adata.cleaned_data["question"])
            adata.cleaned_data["files"] = []
            conn = connect(service_config.answer_system['add_answer'], "POST",
                           data=json.dumps(adata.cleaned_data))
            ans_data = json.loads(conn.content)
        except Exception as exp:
            return JsonResponseServerError({"type": "error", "data": "internal server error"})
        return JsonResponse(ans_data)
    return JsonResponseBadRequest({"type": "error", "data": adata.errors})


@csrf_exempt
@require_POST
def attach_file_question(request, quuid):
    return attach_file(request, quuid, service_config.question_system["attache"],
                       service_config.question_system["is_exist"], 'question')

@csrf_exempt
@require_POST
def attach_file_answer(request, quuid, auuid):
    try:
       uuid.UUID(quuid)
    except ValueError:
        return JsonResponseBadRequest({'type': "error", "data": "incorect uuid of question"})
    try:
        conn = connect(service_config.question_system['is_exist'] % (quuid,), "GET")
        if conn.status_code != 200:
            return JsonResponseNotFound({"type": "error", "data": "question not found"})
    except Exception as exp:
        return JsonResponseServerError({'type': "error", "data": exp})
    return attach_file(request, auuid, service_config.answer_system["attache"],
                       service_config.answer_system["is_exist"], 'answer')

def attach_file(request, quuid, system_attach, system_exist, system_object):
    try:
        js = json.loads(request.POST['info'])
    except:
        return JsonResponseBadRequest({"type": "error", "data": "request must containing in body json object"})
    qdata = forms.Attach(js)
    if qdata.is_valid():
        try:
            conn = connect(system_exist % (quuid), "GET")
            if conn.status_code == 200:
                conn = connect(service_config.file_system["add_file"], "POST",
                               files={"file": request.FILES['file']}, data={"info": json.dumps(js)})
                if conn.status_code == 200:
                    finfo = json.loads(conn.content)
                    conn = connect(system_attach % (quuid, finfo['uuid']), "POST")
                    if conn.status_code == 200:
                        return JsonResponse({"type": "ok", 'file_info': finfo})
                    else:
                        conn = connect(service_config.file_system["delete_file"] % (finfo['uuid']), "DELETE")
                        return JsonResponseServerError({'type': "error", "data": json.loads(conn.content)})
                else:
                    return JsonResponseServerError({'type': "error", "data": json.loads(conn.content)})
            else:
                return JsonResponseNotFound({'type': "error", "data": f"not found {system_object} this uuid"})
        except Exception as exp:
            return JsonResponseServerError({"type": "error", "data": str(exp)})



    return JsonResponseBadRequest({"type": "error", "data": qdata.errors})

@csrf_exempt
@require_http_methods(['GET', 'DELETE'])
def file_worker(request):
    if request.method == "GET":
        return download_file_controller(request)
    else:
        return delete_file_controller(request)


@csrf_exempt
@require_GET
def download_file_controller(request, fuuid):
    try:
        uuid.UUID(fuuid)
    except ValueError:
        return JsonResponseBadRequest({"type": "error", "data": "incorrect uuid of file"})
    try:
        fname = download_file(service_config.file_system['download'] % (fuuid,))
    except Exception as exp:
        return JsonResponseServerError({"type": "error", "data": "internal server error"})

    return FileResponse(open(fname, "br"))

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_file_controller(request, try_delete_files_in_services = True):
    try:
        data = forms.uuid_list(json.loads(request.body))
    except ValueError:
        return JsonResponseBadRequest({"type": "error", "data": "request mast be containing json object"})
    if data.is_valid():
        for fuuid in data.cleaned_data['uuid']:
            try:
                if try_delete_files_in_services:
                    conn = connect(service_config.question_system['try_delete_file'] % (fuuid,), "DELETE")
                    if conn.status_code == 404:#файл не принадлежит ни одному вопросу
                        conn = connect(service_config.answer_system['try_delete_file'] % (fuuid,), "DELETE")
                        if conn.status_code != 200: #либо файл не принадлежит ни одному ответу, либо ошибка на срвисе
                            return JsonResponseServerError({"type": "error", "data": "impossible delete file"})
                conn = connect(service_config.file_system['delete_file'] % (fuuid,), "DELETE")
                if conn.status_code != 200:
                    return JsonResponseServerError({'type': "error", "data": "impossible delete file"})
            except Exception as exp:
                return JsonResponseServerError({"type": "error", "data": str(exp)})
        return JsonResponse({'type': "ok", "data": "file was be removed"})
    else:
        return JsonResponseBadRequest({"type": "error", "data": data.errors})



@require_http_methods(["DELETE"])
@csrf_exempt
def delete_answers(request, question_uuid):
    try:
        data = forms.uuid_list(json.loads(request.body))
    except ValueError:
        return JsonResponseBadRequest({"type": "error", "data": "body of request must containing a json object"})
    try:
        uuid.UUID(question_uuid)
    except ValueError:
        return JsonResponseBadRequest({"type": "error", "data": "incorrect question uuid"})
    try:
        conn = connect(service_config.answer_system['check_belong_answers'] % (question_uuid,),
                       "GET", data=request.body)
    except Exception as exp:
        return JsonResponseServerError({'type': "error", "data": str(exp)})
    if conn.status_code == 404:
        return JsonResponseBadRequest({"type": "error", "data": "this answers don't belong this question"})
    if data.is_valid():
        for auuid in data.cleaned_data['uuid']:
            try:
                conn = connect(service_config.answer_system['delete_and_return_files'] % (auuid), "DELETE")
                if conn.status_code == 200:
                    request_for_del_files = HttpRequest()
                    request_for_del_files._body = json.dumps({"uuid": json.loads(conn.content)["files"]})
                    request_for_del_files.method = "DELETE"
                    return delete_file_controller(request_for_del_files, False)
                else:
                    return JsonResponseServerError({"type": "error", "data": "error of delete files"})
            except Exception as exp:
                return JsonResponseServerError({"type": "error", "data": str(exp)})
    return JsonResponseBadRequest({"type": "error", "data": data.errors})


def delete_question(request, question_uuid):
    try:
        uuid.UUID(question_uuid)
    except ValueError:
        return JsonResponseBadRequest({"type": "error", "data": "incorrect uuid of answer"})
    conn = connect(service_config.question_system["is_exist"] % (question_uuid,), "GET")
    if conn.status_code == 200:
        conn = connect(service_config.answer_system['get_answers'] % (question_uuid,), "GET")
        if conn.status_code == 200:
            if len(json.loads(conn.content)["uuid"]) != 0:
                request_for_del_answers = HttpRequest()
                request_for_del_answers._body = conn.content
                request_for_del_answers.method = "DELETE"
                response = delete_answers(request_for_del_answers, question_uuid)
                if response.status_code != 200:
                    return JsonResponseServerError({"type": "error", "data": "answers of question delete error!"})
        conn = connect(service_config.question_system['delete_and_return_files'] % (question_uuid,), "DELETE")
        if conn.status_code == 200:
            try:
                files_list = json.loads(conn.content)["uuid"]
                if len(files_list) != 0:
                    request_for_del_files = HttpRequest()
                    request_for_del_files._body = json.dumps({"uuid": files_list})
                    request_for_del_files.method = "DELETE"
                    return delete_file_controller(request_for_del_files, False)
                else:
                    return JsonResponse({"type": "ok", "data": "question was be removed"})
            except Exception as exp:
                return JsonResponseServerError({"type": "error", "data": str(exp)})
        else:
            return JsonResponseServerError({"type": "error", "data": "question delete error!"})
    else:
        return JsonResponseNotFound({"type": "error", "data": "question with uuid not found"})
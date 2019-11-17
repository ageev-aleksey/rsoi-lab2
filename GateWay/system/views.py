from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.http import JsonResponse, HttpResponse
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

def connect(service_path,method, timeout=5, data = None, params = None):
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
            r = con(service_path, timeout=timeout, params=params, data=data)
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
        return JsonResponseNotFound({"type": "ok", "data": "answers not found"})
    return JsonResponse({"type": "ok"})


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
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.http import JsonResponse
import logging
import requests
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
        raise ConnectionError("Request timed out")
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
    except ConnectionError:
        return JsonResponseServerError({"type": "error", "data": "Unable to get a list of questions"})
    if rquestions.status_code == 200:
        try:
            data = rquestions.json()
            rcount_answers = connect(service_config.answer_system["count_answers_question"],
                                     "GET", data=data["questions"])
            print(rcount_answers.status_code)
            if rcount_answers.status_code == 200:
                count = data["count"]
                res = {"type": "questions_paginate", "page": page, "pages": rquestions["pages"],
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


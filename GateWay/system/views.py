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

def connect(service_path,method, timeout=0.001,**kwargs):
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
            r = con(service_path, timeout=timeout, **kwargs)
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
        rquestions = connect(service_config.question_system["questions_list"], "GET", params={"page": page}).json()
    except ConnectionError:
        return JsonResponseServerError({"type": "error", "data": "Unable to get a list of questions"})
    if rquestions.status_code == 200:
        try:
            rcount_answers = connect(service_config.answer_system["count_answers_question"],
                                     "GET", data=rquestions["questions"]).json()
        except Exception as exp:
            log.exception("Error, get count answers of question. " + str(exp))
    else:
        pass


from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
import uuid as UUID
import logging
import json
from . import models
from . import forms

require_DELETE = require_http_methods(["DELETE"])
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



@require_GET
@csrf_exempt
def get_questions(request):
    """GET
    Response:
        Correct:  Code 200 Ok. Body:
            {"type": "questions_brief_paginate",
            "page": "<page number>", "pages": "<number of pages>",
            "questions": [
                            {
                                "title": "<title>",
                                "brief": "<brief describe>",
                                "author": "<author_uuid>",
                                "num_answers": "<number answers>",
                                "is_correct": "<True or False>"
                                "rating": "<integer number>"
                            }
                         ]
            }
        Error: Code 400 Bad request. Body:
            {"type": "error", "data": "<brief description error>"}"""
    log = logging.getLogger("questions.get_questions")
    log.setLevel(logging.DEBUG)
    log.info("Get questions list")
    try:
        page = int(request.GET['page'])
    except:
        return JsonResponseBadRequest({"type": "error", "data": "error get parameters"})
    data = models.Question.objects.all().order_by("date")
    if data.count() == 0:
        return JsonResponseNoContent({"type": "error", "data": "result after apply this request does not containing data"})
    paginator = Paginator(data, per_page=10)
    if page < 0 or page > paginator.num_pages:
        return JsonResponseNotFound({"type": "error", "data": "page number exceed existing number of pages"})
    brief_list = []
    for el in paginator.page(page):
        brief_list.append(el.brief_to_dict())

    return JsonResponse({"type": "questions_brief_paginate",
                         "page": page,
                         "pages":  paginator.num_pages,
                         "questions": brief_list})


@csrf_exempt
def question(request, uuid):
    if request.method == "GET":
        return get_question_detail_and_answers(request, uuid)
    if request.method == "DELETE":
        return delete_question(request, uuid)

@csrf_exempt
def get_question_detail_and_answers(request, uuid):
    """GET
       Response:
           Correct:  Code 200 Ok. Body:
               {
                "uuid": "<question_uuid>",
                "title": "<question_title>",
                "text": "<question_text>",
                "user": <user_name>,
                "files": [<files_uuid>],
                "tags": [<tags>]
               }
           Error: Code 400 Bad request. Body:
               {"type": "error", "data": "<brief description error>"}
            Error: 405 method note alowed"""
    try:
        uuid = UUID.UUID(uuid)
    except:
        return JsonResponseBadRequest({"type": "error", "data": "incorect uuid of question"})
    print(uuid)
    question = models.Question.objects.filter(uuid = uuid)
    if len(question) == 0:
        return JsonResponseNotFound({"type": "error", "data": "This question Not Found"})
    return JsonResponse(question[0].detail_to_dict())


@require_POST
@csrf_exempt
def add_question2(request):
    """Post
        Body Request:
            {
                "title": "<question title>",
                "text": "<detail describe question>",
                "user": "<user_uuid>",
                "tags": [<list of tags>...]
                "files": [<list of files_uuid>...]
        Response:
            201 Created
            405 method note alowed
    """
    log = logging.getLogger("questions.add_question")
    log.setLevel(logging.DEBUG)
    log.info("add question")
    try:
        data = json.loads(request.body)
    except Exception as exp:
        return JsonResponseBadRequest({"type": "error", "data": "You must send body in json format"})
    # Проверка того, что все поля существуют
    for key in ["title", "text", "user", "tags", "files"]:
        if key not in list(data.keys()):
            return  JsonResponseBadRequest({"type": "error", "data": "You must have key: " + key })
    question = models.Question()
    try:
        question.from_dict(data)
    except Exception as exp:
        return JsonResponseBadRequest({"type": "error", "data": str(exp)})
    question.save(force_insert=True)
    try:
        for fuuid in data['files']:
            f = models.FilesForQuestion(question=question, file_uuid=UUID.UUID(fuuid))
            f.save()
    except ValueError as exp:
        raise ValueError("incorrect file uuid")
    for t in data['tags']:
        tag = models.Tag.objects.filter(tag=t)
        if len(tag) == 0:
            tag = models.Tag(tag=t)
            tag.save()
        else:
            tag = tag[0]
        models.TagsForQuestions(question=question, tag=tag).save()
    return JsonResponseCreated({"type": "ok", "uuid": question.uuid})

@require_POST
@csrf_exempt
def add_question(request):
    """Post
        Body Request:
            {
                "title": "<question title>",
                "text": "<detail describe question>",
                "user": "<user_uuid>",
                "tags": [<list of tags>...]
                "files": [<list of files_uuid>...]
        Response:
            201 Created
            405 method note alowed
            404 bad request
    """
    log = logging.getLogger("questions.add_question")
    log.setLevel(logging.DEBUG)
    log.info("add question")
    try:
        data = json.loads(request.body)
    except Exception as exp:
        return JsonResponseBadRequest({"type": "error", "data": "You must send body in json format"})
    qdata = forms.Question(data)
    if qdata.is_valid():
        question = models.Question()
        question.from_dict(qdata.cleaned_data)
        question.save()
        if "tags" in qdata.cleaned_data:
            for tag in qdata.cleaned_data['tags']:
                t = models.Tag(tag=tag)
                t.save()
                models.TagsForQuestions(tag=t, question=question).save()
    else:
        return JsonResponseBadRequest({"type": "error", "data": qdata.errors})
    return JsonResponseCreated({"type": "ok", "uuid": question.uuid})

@require_DELETE
@csrf_exempt
def delete_question(request, uuid):
    try:
        question = models.Question.objects.filter(uuid=UUID.UUID(uuid))
    except:
        return JsonResponseBadRequest({"type": "error", "data": "incorrect question identificator"})
    if question.count() == 0:
        return JsonResponseNotFound({"type": "error", "data": "qustion with identificator not found"})
    question[0].delete()
    return JsonResponse({"type": "ok"})

@csrf_exempt
@require_POST
def attach_file(request, quuid, fuuid):
    data = {'question': quuid, 'file': fuuid}
    validator = forms.AttachFile(data)
    if validator.is_valid():
        try:
            question = models.Question.objects.get(uuid=validator.cleaned_data['question'])
        except ObjectDoesNotExist as exp:
            return JsonResponseNotFound({'type': 'error', "data": "question with uuid not exists"})
        try:
            models.FilesForQuestion(question=question,
                                    file_uuid=validator.cleaned_data['file']).save(force_insert=True)
        except Exception as exp:
            return JsonResponseServerError({"type": "error", "data": str(exp)})
        return JsonResponse({'type': 'ok'})
    return JsonResponseBadRequest({'type': "error", "data": validator.errors})

@csrf_exempt
@require_GET
def is_exist(request, quuid):
    try:
        quuid = UUID.UUID(quuid)
    except ValueError:
        return JsonResponseBadRequest({"type": "error", "data": "incorrect uuid of question"})
    try:
        models.Question.objects.get(uuid=quuid)
    except ObjectDoesNotExist:
        return JsonResponseNotFound({'type': "ok", "data": "Object don't exist"})
    return JsonResponse({'type': "ok", "data": "Object exist"})

@csrf_exempt
@require_DELETE
def try_delete(reuest, fuuid):
    try:
        fuuid = UUID.UUID(fuuid)
    except ValueError:
        return JsonResponseBadRequest({"type": "error", "data": "incorrect file uuid"})
    file = models.FilesForQuestion.objects.filter(file_uuid=fuuid)
    if file.count() == 0:
        return JsonResponseNotFound({"type": "error", "data": "not found question which belong this file"})
    file[0].delete()
    return JsonResponse({"type": "ok"})


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_and_return_files(request, quuid):
    try:
        quuid = UUID.UUID(quuid)
    except ValueError:
        return JsonResponseBadRequest({"type": "error", "data": "incorrect question uuid"})
    try:
        question = models.Question.objects.get(uuid=quuid)
    except ObjectDoesNotExist:
        return JsonResponseNotFound({"type": "error", "data": "question with uuid not found"})
    files = models.FilesForQuestion.objects.filter(question=question)
    flist = []
    for f in files:
        flist.append(str(f.file_uuid))
    question.delete()
    return JsonResponse({"type": "files_list", "uuid": flist})

#TODO Запрос на добавление ответа к вопросу, завершается без ошибок, но запрос дитального описания вопроса не выводит добавленный ответ
#TODO для 4 лабы использовать redis
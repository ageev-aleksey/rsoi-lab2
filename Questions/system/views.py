from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.core.paginator import Paginator
import uuid as UUID
import json
from . import models

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


@require_GET
@csrf_exempt
def get_questions(request, page=1):
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
    data = models.Question.objects.all()
    if len(data) == 0:
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
               {"type": "question_detail_and_answers_pagination,
               "page": "<page number>", "pages": "<number of pages>",
               "question": {
                                   "title": "<title>",
                                   "text": "<detail describe>",
                                   "user": "<author_uuid>",
                                   "rating": "<integer number>"
                            },
                "answers": [
                                {
                                    "text": "<detail describe>",
                                    "user": "<author_uuid>",
                                    "rating": "<integer number>"
                                    "isCorrect": "<True or False>"
                                }
                            ]

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

#TODO сделать возможность добавление uuid файлов
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
            }
        Response:
            201 Created
            405 method note alowed
    """

    try:
        data = json.loads(request.body)
    except Exception as exp:
        return JsonResponseBadRequest({"type": "error", "data": "You must send body in json format"})
    # Проверка того, что все поля существуют
    for key in ["title", "text", "user", "tags"]:
        if key not in list(data.keys()):
            return  JsonResponseBadRequest({"type": "error", "data": "You must have key: " + key })
    question = models.Question()
    try:
        question.from_dict(data)
    except Exception as exp:
        return JsonResponseBadRequest({"type": "error", "data": str(exp)})
    question.save(force_insert=True)
    for t in data['tags']:
        tag = models.Tag.objects.filter(tag=t)
        if len(tag) == 0:
            tag = models.Tag(tag=t)
            tag.save()
        else:
            tag = tag[0]
        models.TagsForQuestions(question=question, tag=tag).save()
    return JsonResponseCreated({"type": "ok", "uuid": question.uuid})

@require_DELETE
@csrf_exempt
def delete_question(request, uuid):
    try:
        question = models.Question.objects.filter(uuid=UUID.UUID(uuid))
    except:
        return JsonResponseBadRequest({"type": "error", "data": "incorrect question identificator"})
    if len(question) == 0:
        return JsonResponseNotFound({"type": "error", "data": "qustion with identificator not found"})
    question[0].delete()
    return JsonResponse({"type": "ok"})

@require_POST
@csrf_exempt
def add_answer_to_question(request, uuid):
    """ POST
        Request Body:
        {
            "text": "<text answer>",
            "user": "<uuid author of answer>",
            "files": [<uuid files>...]
        }
    """
    try:
        data = json.loads(request.body)
    except:
        return JsonResponseBadRequest({"type": "error", "data": "You must send body in json format"})
   # проверка всех uuid
    try:
        user_uuid = UUID.UUID(uuid)
        files_uuid = []
        for f in data["files"]:
            files_uuid.append(UUID.UUID(f))
    except:
        return JsonResponseBadRequest({"type": "error", "data": "incorrect object identificator"})

    question = models.Question.objects.filter(uuid=user_uuid)

    try:
        if len(question) == 0:
            return JsonResponseNotFound({"type": "error", "data": "qustion with identificator not found"})
        question = question[0]
        answer = models.Answer(question=question)
        answer.from_dict(data)
        answer.save()
        for fuuid in files_uuid:
            models.FilesForAnswer(answer=answer, file_uuid=fuuid).save()
        return JsonResponse({"type": "ok", 'uuid':  answer.uuid})
    except Exception as exp:
        return JsonResponseBadRequest({"type": "error", "data": str(exp)})
    return JsonResponseBadRequest({"type": "error"})


@csrf_exempt
def delete_answer(response,question_uuid, answer_uuid):
    """ DELETE:
        Response
            -200:
                {"type": "ok"}
            -400:
                {"type": "error", "data": "incorrect question identificator"}
                {"type": "error", "data": "incorrect answer identificator"}
            -404:
                {"type": "error", "data": "incorrect question identificator"}


    """

    try:
        question  = models.Question.objects.filter(uuid=UUID.UUID(question_uuid))
    except:
        return JsonResponseBadRequest({"type": "error", "data": "incorrect question identificator"})
    if len(question) == 0:
        return JsonResponseNotFound({"type": "error", "data": "question with uuid not found"})
    try:
        answer = models.Answer.objects.filter(uuid=UUID.UUID(answer_uuid))
    except:
        return JsonResponseBadRequest({"type": "error", "data": "incorrect answer identificator"})
    if len(answer) == 0:
        return JsonResponseNotFound({"type": "error", "data": "answer with uuid not found"})
    if answer[0].question != question[0]:
        return JsonResponseBadRequest({"type": "error", "data": "uuid of answer not match uuid of question"})
    answer.delete()
    return JsonResponse({"type": "ok"})
#TODO Запрос на добавление ответа к вопросу, завершается без ошибок, но запрос дитального описания вопроса не выводит добавленный ответ
#TODO для 4 лабы использовать redis
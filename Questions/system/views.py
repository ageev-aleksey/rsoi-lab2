from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.core.paginator import Paginator
import uuid as UUID
from . import models
# Create your views here.
class JsonResponseBadRequest(JsonResponse):
    status_code = 400
class JsonResponseNotFound(JsonResponse):
    status_code = 404
class JsonResponseNoContent(JsonResponse):
    status_code = 203


@require_GET
@csrf_exempt
def get_questions(request, page):
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
    paginator = Paginator(models.Question.objects.all())
    if page < 0 or page > paginator.num_pages:
        return JsonResponseBadRequest({"type": "error", "data": "page number exceed existing number of pages"})
    brief_list = []
    for el in paginator.page(page):
        brief_list.append(el.brief_describe_to_dict())

    return JsonResponse({"type": "questions_brief_paginate",
                         "page": page,
                         "pages":  paginator.num_page,
                         "questions": brief_list})

def get_question_detail_and_answers(request, uuid):
    """GET
       Response:
           Correct:  Code 200 Ok. Body:
               {"type": "question_detail_and_answers_pagination,
               "page": "<page number>", "pages": "<number of pages>",
               "question": {
                                   "title": "<title>",
                                   "text": "<detail describe>",
                                   "author": "<author_uuid>",
                                   "rating": "<integer number>"
                            },
                "answers": [
                                {
                                    "text": "<detail describe>",
                                    "author": "<author_uuid>",
                                    "rating": "<integer number>"
                                    "isCorrect": "<True or False>"
                                }
                            ]

               }
           Error: Code 400 Bad request. Body:
               {"type": "error", "data": "<brief description error>"}"""
    uuid = UUID.UUID(uuid)
    print(uuid)
    question = models.Question.objects.filter(uuid = uuid)
    if len(question) == 0:
        return JsonResponseNotFound({"type": "error", "data": "This question Not Found"})
    return JsonResponse(question[0].detail_to_dict())




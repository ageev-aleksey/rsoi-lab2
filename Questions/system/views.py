from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.core.paginator import Paginator
from . import models
# Create your views here.
class JsonResponseBadRequest(JsonResponse):
    status_code = 400


@require_GET
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
    paginator = Paginator(models.Question.objects.all());
    if page < 0 or page > paginator.num_pages:
        return JsonResponseBadRequest({"type": "error", "data": "page number exceed existing number of pages"})
    brief_list = []
    for el in paginator.page(page):
        brief_list.append(el.brief_describe_to_dict())

    return JsonResponse({"type": "questions_brief_paginate",
                         "page": page,
                         "pages":  paginator.num_page,
                         "questions": brief_list})




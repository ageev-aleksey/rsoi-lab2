from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
import json
import uuid as UUID
from . import forms
from . import models

require_DELETE = require_http_methods(["DELETE"])



# Create your views here.
class JsonResponseBadRequest(JsonResponse):
    status_code = 400
class JsonResponseNotFound(JsonResponse):
    status_code = 404
class JsonResponseMethodNotAllowed(JsonResponse):
    status_code = 405
    def __init__(self, permitted_methods, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self['Allow'] = ', '.join(permitted_methods)

class JsonResponseNoContent(JsonResponse):
    status_code = 203
class JsonResponseCreated(JsonResponse):
    status_code = 201
class JsonResponsePartialContent(JsonResponse):
    status_code = 206

def required_http_methods_json(allowed_request):
    def decorator(fn):
        def wrapped(request, *args, **kwargs):
            if request.method in allowed_request:
                return fn(request, *args, **kwargs)
            else:
                return JsonResponseMethodNotAllowed(allowed_request, {"type": "error", "data":
                    "this url path not allowed method is " + request.method})
        return wrapped
    return decorator


# Create your views here.
@require_POST
@csrf_exempt
def add_answer(request):
    """ POST
        Request Body:
        {
            "text": "<text answer>",
            "author": "<author_name>",
            "question": "<uuid of question>",
            "files": [<uuid files>...]
        }
    """
    try:
        data = json.loads(request.body)
    except:
        return JsonResponseBadRequest({"type": "error", "data": "You must send body in json format"})
   # проверка всех uuid
    try:
        question_uuid = UUID.UUID(data['question'])
    except ValueError:
        return JsonResponseBadRequest({"type": "error", "data": "incorrect object identificator"})
    except KeyError:
        return JsonResponseBadRequest({"type": "error", "data": "json request must containing a field 'question'"})
    try:
        files_uuid = []
        for f in data["files"]:
            files_uuid.append(UUID.UUID(f))
    except ValueError:
        return JsonResponseBadRequest({"type": "error", "data": "incorrect uuid of file"})
    except KeyError:
        return JsonResponseBadRequest({"type": "error", "data": "json request must containing a field 'files'"})
    except TypeError:
        return JsonResponseBadRequest({"type": "error", "data": " field 'files' must have type a list"})
    try:
        answer = models.Answer()
        answer.from_dict(data)
        answer.save()
        for fuuid in files_uuid:
            models.FilesForAnswer(answer=answer, file_uuid=fuuid).save()
        return JsonResponseCreated({"type": "ok", 'uuid':  answer.uuid})
    except Exception as exp:
        raise exp
        return JsonResponseBadRequest({"type": "error", "data": str(exp)})

@require_POST
@csrf_exempt
def add_answer_test(request):
    """ POST
        Request Body:
        {
            "text": "<text answer>",
            "author": "<author_name>",
            "question": "<uuid of question>",
            "files": [<uuid files>...]
        }
    """
    j = json.loads(request.body)
    print(j)
    data = forms.AnswerForm(j)
    if data.is_valid():
        print(data.cleaned_data)
    print(data.errors)
    return JsonResponse({'ok': "ok"})

@csrf_exempt
def get_or_del_answer(request, uuid):
    if request.method == "GET":
        return get_answer(request, uuid)
    if request.method == "DELETE":
        return delete_answer(request, uuid)
    return JsonResponseMethodNotAllowed({"type": "error",
                                         "data": "this url path not allowed method is " + request.method},
                                        ["GET", "DELETE"])

@csrf_exempt
def get_answers_page(request):
    """Request
    {
        "uuid": [<question uuid>]
    }"""
    #try:
        #data = json.loads(request.body)
   # except:
        #return JsonResponseBadRequest({"type": "error", "data": "You must send body in json format"})
    data_response = {"type": "answers_list_pagination", "page": 0, "pages": 0, "answers": []}
    try:
         paginator = Paginator(models.Answer.objects.filter(question_uuid=request.GET["question"]), 3)
         try:
             if int(request.GET['page']) > paginator.num_pages:
                 return JsonResponseNotFound({"type": "error", "data": "this page for answer not exists"})
         except KeyError:
            return JsonResponseBadRequest({"type": "error", "data": "when accessing the resource, you must pass "
                                                                    "a get parametrs for page"})
         except Exception as exp:
             return JsonResponseBadRequest({"type": "error", "data": "get paramet 'page' incorrect: " + str(exp) })
         for answr in paginator.page(request.GET['page']):
             data_response["answers"].append(answr.to_dict())
         data_response["page"] = request.GET['page']
         data_response["pages"] = paginator.num_pages
    except ObjectDoesNotExist as exp:
        data_response["errors"].append(str(exp))
        i = 1 + 1
    except KeyError:
        return JsonResponseBadRequest({"type": "error", "data": "Json must have containing fild 'uuid'"})
    return JsonResponse(data_response)


def get_answer(request, uuid):
    try:
        ans = take_answer_from_db(uuid)
    except Exception as exp:
        return JsonResponseBadRequest({"type": "error", "data:": str(exp)})
    return JsonResponse({"type": "answer", "answer": ans})



def take_answer_from_db(uuid):
    try:
        uuid = UUID.UUID(uuid)
    except ValueError:
        raise ValueError("incorrect uuid of answer")
        #return JsonResponseBadRequest({"type": "error", "data": "incorrect uuid of answer"})
    try:
        answer = models.Answer.objects.get(uuid=uuid)
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist("answer with uuid " + uuid + " not found")
        #return JsonResponseNotFound({"type": "error", "data": "answer with uuid " + uuid + " not found"})
    return answer.to_dict()

@csrf_exempt
def delete_answer(response,answer_uuid):
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
        answer = models.Answer.objects.filter(uuid=UUID.UUID(answer_uuid))
    except:
        return JsonResponseBadRequest({"type": "error", "data": "incorrect uuid of answer"})
    if len(answer) == 0:
        return JsonResponseNotFound({"type": "error", "data": "answer with uuid not found"})
    answer.delete()
    return JsonResponse({"type": "ok"})

@csrf_exempt
def count_answers(request):
    try:
        question_uuid = UUID.UUID(request.GET['question'])
    except KeyError:
        return JsonResponseBadRequest({"type": "error","data": "you must send get parameter a 'question'"})
    except ValueError:
        return JsonResponseBadRequest({"type": "error", "data": "get parameter a 'question' must have type UUID4"})
    answers = models.Answer.objects.filter(question_uuid=question_uuid)
    return JsonResponse({"type": "ok", "count": answers.count()})

@csrf_exempt
@require_GET
def count_answers_for_list_questions(request):
    try:
        data = json.loads(request.body)
    except json.decoder.JSONDecodeError:
        return JsonResponseBadRequest({"type": "error", "data": "body of query must have containing json object"})
    try:
        res = {"type": "count_answers_list", "count": []}
        for quuid in data['questions']:
            res['count'].append(models.Answer.objects.filter(question_uuid=UUID.UUID(quuid)).count())
    except KeyError:
        return JsonResponseBadRequest({"type": "error", "data": "json must have a field 'questions'"})
    except ValueError:
        return JsonResponseBadRequest({"type": "error", "data": "get parameter a 'question' must have type UUID4"})
    return JsonResponse(res)


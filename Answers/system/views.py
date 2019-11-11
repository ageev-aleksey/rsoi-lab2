from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST, require_http_methods
import json
import uuid as UUID
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
        return JsonResponse({"type": "ok", 'uuid':  answer.uuid})
    except Exception as exp:
        return JsonResponseBadRequest({"type": "error", "data": str(exp)})


@csrf_exempt
def get_or_del_answer(request, uuid):
    if request.method == "GET":
        return get_answer(request, uuid)
    if request.method == "DELETE":
        return delete_answer(request, uuid)
    return JsonResponseMethodNotAllowed(["GET", "DELETE"], {"type": "error", "data":
                    "this url path not allowed method is " + request.method})

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
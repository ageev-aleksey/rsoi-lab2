from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
import json
import uuid as UUID
from . import forms
from . import models
from .service_config import *

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
class JsonResponseServerError(JsonResponse):
    status_code = 500

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
    log = logging.getLogger("add_answer")
    log.info("began perform request on create new answer")
    try:
        data = json.loads(request.body)
    except:
        log.error("was sent incorrect body of reqest: %s", request.body)
        return JsonResponseBadRequest({"type": "error", "data": "You must send body in json format"})
   # проверка всех uuid
    try:
        question_uuid = UUID.UUID(data['question'])
    except ValueError:
        log.error("Invalid UUID of answer: %s", data['question'])
        return JsonResponseBadRequest({"type": "error", "data": "incorrect object identificator"})
    except KeyError:
        log.error("not was got uuid of question from client")
        return JsonResponseBadRequest({"type": "error", "data": "json request must containing a field 'question'"})
    try:
        files_uuid = []
        for f in data["files"]:
            files_uuid.append(UUID.UUID(f))
    except ValueError as exp:
        log.error("Invalid UUID of file: %s", str(exp))
        return JsonResponseBadRequest({"type": "error", "data": "incorrect uuid of file"})
    except KeyError:
        log.error("json don't containing a field 'files': %s", request.body)
        return JsonResponseBadRequest({"type": "error", "data": "json request must containing a field 'files'"})
    except TypeError:
        log.error("field of json have invalid type: %s", request.body)
        return JsonResponseBadRequest({"type": "error", "data": " field 'files' must have type a list"})
    try:
        answer = models.Answer()
        answer.from_dict(data)
        answer.save()
        for fuuid in files_uuid:
            models.FilesForAnswer(answer=answer, file_uuid=fuuid).save()
        log.info("answer %s created", str(answer.uuid))
        return JsonResponseCreated({"type": "ok", 'uuid':  answer.uuid})
    except Exception as exp:
        log.exeption(str(exp))
        return JsonResponseBadRequest({"type": "error", "data": str(exp)})

'''X
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
'''

@csrf_exempt
@require_http_methods(["GET", "DELETE"])
def answers_worker(request, uuid):
    if request.method == "GET":
        return get_answer(request, uuid)
    if request.method == "DELETE":
        return delete_answer(request, uuid)
'''
def update_answer(request, uuid):
    try:
        uuid = UUID.UUID(uuid)
    except ValueError:
        return JsonResponseBadRequest({"type": "error", "data": "inocrrect uuid of answer"})
    try:
        answer = models.Answer.objects.get(uuid=uuid)
        answer.text = json.loads(request.body)['text']
        answer.save()
        return JsonResponse({"type": "ok", "data": "answer update"})
    except ObjectDoesNotExist:
        return JsonResponseNotFound({"type": "error", "data": "answer with uuid not found"})
    except KeyError as exp:
        return JsonResponseBadRequest({"type": "error", "data": str(exp)})
'''


@csrf_exempt
@require_GET
def get_answers_page(request):
    """Request
    {
        "uuid": [<question uuid>]
    }"""
    log = logging.getLogger("get_answers_page")
    log.info("begun perform request for create json of paginate list of answers")
    #try:
        #data = json.loads(request.body)
   # except:
        #return JsonResponseBadRequest({"type": "error", "data": "You must send body in json format"})
    data_response = {"type": "answers_list_pagination", "page": 0, "pages": 0, "answers": []}
    page = int(request.GET['page'])
    try:
         paginator = Paginator(models.Answer.objects.filter(question_uuid=request.GET["question"]).order_by('date'), 3)
         try:
             if page > paginator.num_pages or page < 0:
                 log.error("invalid number page of answers: %d", page)
                 return JsonResponseNotFound({"type": "error", "data": "this page for answer not exists"})
         except KeyError:
             log.error("not was got query parameter 'get'")
             return JsonResponseBadRequest({"type": "error", "data": "when accessing the resource, you must pass "
                                                                     "a get parametrs for page"})
         except Exception as exp:
             log.exception(str(exp))
             return JsonResponseBadRequest({"type": "error", "data": "get paramet 'page' incorrect: " + str(exp) })
         for answr in paginator.page(page):
             data_response["answers"].append(answr.to_dict())
         data_response["page"] = page
         data_response["pages"] = paginator.num_pages
    except ObjectDoesNotExist as exp:
        log.warning(str(exp))
        data_response["errors"].append(str(exp))
    except KeyError as exp:
        log.error(str(exp))
        return JsonResponseBadRequest({"type": "error", "data": str(exp)})
    log.info("json of list answers created")
    return JsonResponse(data_response)

@require_GET
@csrf_exempt
def get_answer(request, uuid):
    try:
        ans = take_answer_from_db(uuid)
    except Exception as exp:
        return JsonResponseBadRequest({"type": "error", "data:": str(exp)})
    return JsonResponse({"type": "answer", "answer": ans})



def take_answer_from_db(uuid):
    log = logging.getLogger("take_answer_from_db")
    log.info("began perform request for get answers")
    try:
        uuid = UUID.UUID(uuid)
    except ValueError:
        log.error('invalid uuid of answer: %s', uuid)
        raise ValueError("incorrect uuid of answer")
        #return JsonResponseBadRequest({"type": "error", "data": "incorrect uuid of answer"})
    try:
        answer = models.Answer.objects.get(uuid=uuid)
    except ObjectDoesNotExist:
        log.error("answer with uuid %s not found", uuid)
        raise ObjectDoesNotExist("answer with uuid " + str(uuid) + " not found")
        #return JsonResponseNotFound({"type": "error", "data": "answer with uuid " + uuid + " not found"})
    log.info("answer %s was be got", uuid)
    return answer.to_dict()

@csrf_exempt
@require_http_methods(["DELETE"])
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
    log = logging.getLogger("delete_answer")
    log.info("began perform request for delete answer")
    try:
        answer = models.Answer.objects.filter(uuid=UUID.UUID(answer_uuid))
    except:
        log.error("invalid uuid of answer: %s", answer_uuid)
        return JsonResponseBadRequest({"type": "error", "data": "incorrect uuid of answer"})
    if answer.count() == 0:
        log.error("answer %s not found", answer_uuid)
        return JsonResponseNotFound({"type": "error", "data": "answer with uuid not found"})
    answer.delete()
    log.info("answer was be deleted")
    return JsonResponse({"type": "ok"})

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_answer_and_return_files(response, answer_uuid):
    log = logging.getLogger("delete_answer_and_return_files")
    log.info("began perform request for delete answers with returning files list")
    try:
        UUID.UUID(answer_uuid)
    except ValueError:
        log.error("invalid uuid of answer^ %s", answer_uuid)
        return JsonResponseBadRequest({"type": "error", "data": "incorrect uuid of answer"})
    files = models.FilesForAnswer.controller.get_files(answer_uuid)
    res = delete_answer(response,answer_uuid)
    if res.status_code == 200:
        log.info("answer was be deleted and returning files list")
        return JsonResponse({"type": "ok", "files": files})
    else:
        return res

def check_belong_answers(request, question_uuid):
    log = logging.getLogger("check_belong_answers")
    log.info("began perform request for checcking belong answers on question %s", question_uuid)
    try:
        question_uuid = UUID.UUID(question_uuid)
    except ValueError:
        log.error("invalid uuid of question: %s", question_uuid)
        return JsonResponseBadRequest({"type": "error", "data": "incorrect question uuid"})
    try:
        data = forms.uuid_list(json.loads(request.body))
    except json.decoder.JSONDecodeError:
        log.error('request body containing invalid json object')
        return JsonResponseBadRequest({"type": "error", "data": 'body of rquest must containing a json object'})
    except Exception as exp:
        log.exception(str(exp))
        return JsonResponseBadRequest({"type": "error", "data": str(exp)})
    if data.is_valid():
        if models.Answer.controller.check_answers_qestion_belong(data.cleaned_data['uuid'], question_uuid):
            log.info("answers  belong  question %s", str(data.cleaned_data['uuid']), question_uuid)
            return JsonResponse({"type": "ok", "data": "answers belong this question"})
        else:
            log.error("answers %s don't belong question %s", data.cleaned_data['uuid'], question_uuid)
            return JsonResponseNotFound({"type": "ok", "data": "answers don't belong this question"})
    return JsonResponseBadRequest({'type': "error", "data:": data.errors})

@csrf_exempt
@require_GET
def count_answers(request):
    log = logging.getLogger("count_answers")
    log.info("began perform question of counting answers of question")
    try:
        question_uuid = UUID.UUID(request.GET['question'])
    except KeyError:
        log.error("request without get parametr 'question'")
        return JsonResponseBadRequest({"type": "error", "data": "you must send get parameter a 'question'"})
    except ValueError:
        log.error("invalid get parametr 'question' %s", request.GET['question'])
        return JsonResponseBadRequest({"type": "error", "data": "get parameter a 'question' must have type UUID4"})
    answers = models.Answer.objects.filter(question_uuid=question_uuid)
    return JsonResponse({"type": "ok", "count": answers.count()})

@csrf_exempt
def count_answers_for_list_questions(request):
    log = logging.getLogger("count_answers_for_list_questions")
    log.info("began perform question of counting answers of list questions")
    try:
        data = json.loads(request.body)
    except json.decoder.JSONDecodeError:
        log.error("invalid body of request %s",request.body)
        return JsonResponseBadRequest({"type": "error", "data": "body of query must have containing json object"})
    try:
        res = {"type": "count_answers_list", "count": []}
        for quuid in data['questions']:
            res['count'].append(models.Answer.objects.filter(question_uuid=UUID.UUID(quuid)).count())
    except KeyError:
        log.error("json object don't contain field 'questions'")
        return JsonResponseBadRequest({"type": "error", "data": "json must have a field 'questions'"})
    except ValueError:
        log.error("invalid get parametr 'question' %s", request.GET['question'])
        return JsonResponseBadRequest({"type": "error", "data": "get parameter a 'question' must have type UUID4"})
    return JsonResponse(res)


@csrf_exempt
def is_exist(request, auuid):
    log = logging.getLogger("is_exist")
    log.info("began perform request for checking for the existence of an answer")
    try:
        auuid = UUID.UUID(auuid)
    except ValueError:
        log.error("invalid uuid of answer %s",  auuid)
        return JsonResponseBadRequest({"type": "error", "data": "incorrect uuid of answer"})
    try:
        models.Answer.objects.get(uuid=auuid)
    except ObjectDoesNotExist:
        log.info("answer %s not found", auuid)
        return JsonResponseNotFound({'type': "ok", "data": "Object don't exist"})
    log.info("answer %s founded", auuid)
    return JsonResponse({'type': "ok", "data": "Object exist"})

@csrf_exempt
@require_POST
def attach_file(request, auuid, fuuid):
    log = logging.getLogger("attach_file")
    log.info("began perform request on attaching file ti answer")
    data = {'answer': auuid, 'file': fuuid}
    validator = forms.AttachFile(data)
    if validator.is_valid():
        try:
            answer = models.Answer.objects.get(uuid=validator.cleaned_data['answer'])
        except ObjectDoesNotExist as exp:
            log.error('answer %s not found'.  auuid)
            return JsonResponseNotFound({'type': 'error', "data": "answer with uuid not exists"})
        try:
            models.FilesForAnswer(answer=answer, file_uuid=validator.cleaned_data['file']).save(force_insert=True)
        except Exception as exp:
            log.exception(str(exp))
            return JsonResponseServerError({"type": "error", "data": str(exp)})
        return JsonResponse({'type': 'ok'})
    return JsonResponseBadRequest({'type': "error", "data": validator.errors})


@csrf_exempt
@require_DELETE
def try_delete_file(reuest, fuuid):
    log = logging.getLogger("try_delete_file")
    log.info("began perform request for trying delete file %s", fuuid)
    try:
        fuuid = UUID.UUID(fuuid)
    except ValueError:
        log.error("invalid uuid of file %s", fuuid)
        return JsonResponseBadRequest({"type": "error", "data": "incorrect file uuid"})
    file = models.FilesForAnswer.objects.filter(file_uuid=fuuid)
    if file.count() == 0:
        log.info("file %s not found", fuuid)
        return JsonResponseNotFound({"type": "error", "data": "not found answer which belong this file"})
    file[0].delete()
    log.info("file deleted")
    return JsonResponse({"type": "ok"})

@csrf_exempt
@require_GET
def get_answers_of_question(request, question_uuid):
    log = logging.getLogger("get_answers_of_question")
    log.info("began perform request for got answers list of question %s", question_uuid)
    try:
        question_uuid = UUID.UUID(question_uuid)
    except ValueError:
        log.error("invalid uuid of question %s", fuuid)
        return JsonResponseBadRequest({"type": "error", "data": "incorrect uuid of question"})
    answers = models.Answer.objects.filter(question_uuid=question_uuid)
    uuid_list = []
    for answ in answers:
        uuid_list.append(answ.uuid)
    log.info("list answers of question created")
    return JsonResponse({"type": "answers_uuid", "uuid": uuid_list})
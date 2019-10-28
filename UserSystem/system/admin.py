from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
# Register your models here.



def get_question_brief(request):
    """POST: {uuid: <uuid_question>}"""
    pass


def get_question_full(request):
    """POST: {uuid: <uuid_question>}"""
    pass

def get_questins_list(request):
    """GET"""
    pass

def add_question(request):
    """POST: {title, brief, text}"""
    pass

def delete_question(request):
    """POST: {uuid}"""
    pass


def add_answer_to_question(request):
    """POST: {uuid: <question_uuid>, text: <text of answer>}"""
    pass

def delete_answer_from_question(request):
    """POST: {uuid_answer}"""
    pass

def get_answers_for_question(request):
    """POST: {uuid_question}"""
    pass
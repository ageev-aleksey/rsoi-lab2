from django.shortcuts import render
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import hashlib
# Create your views here.
def get_json(request):
    if request.content_type == 'application/json':
        return json.loads(request.body)
    else:
        raise ValueError("request json - wrong!")
class JsonResponseRequestError(HttpResponse):
    def __init__(self):
        HttpResponse.__init__(self, "{'type': 'error', 'data': 'wrong request'}")

@csrf_exempt
def singup(request):
    try:
        if request.method == 'POST':
            data = get_json(request)
            response = JsonResponse(data)
            print(hashlib.sha256(data))
           # response.set_cookie('session', hashlib.sha256(data))
            return response
        else:
            return JsonResponseRequestError()
    except:
        print("++ERROR++")
        return JsonResponseRequestError()

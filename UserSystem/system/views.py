from django.shortcuts import render
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import hashlib
from . import models
from . import JWT

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


class Authorize:
    '''Авторизация пользователя:
        Request: Singin
            {
	            "login" : "<login>",
	            "pass": "<password>"
            }

            Response:
            {
	            type: "ok",
	            token: "<JWT>"
            }
             {
	            type: "error",
	            id: 1,
	            desc: "wrong login or password"
             }
             Access resurce:
             {'''
    def __init__(self, request):
        if self.request.method == 'POST':
            self.data = json.dumps(request.body)
            self.response = {}
    '''
    def createUser(self):
        if self._request.method == "POST":
            jdata = json.loads(self._request.body)
            user = models.User()
            '''
    def isAuthorize(self):
        '''ПРоверка аторизованности выполнятеся с помощью JWT токена
        JWT:
        |       header = {"alg": "HS256", "typ": "JWT" }
        |       payload = {"login": "login"}
        |       token = base64(header).base64(payload)
            JWT = token.HMAC-SH256(token, secret_key)
        '''
        try:
            if JWT.testJWT(self.data['jwt']):
                user_sess = models.UserSession.objects.filter(
                    user = models.User.objects.filter(login = )
                )
        except:
            return False

    def authorize(self):
        '''Функция проверяющая полномочия неизвествного пользователя по логину и паролю
        '''
        try:
            user = models.User.objects.filter(nikname = self.data['login'])
            if (len(user) == 1) and (user[0].password == hashlib.sha256(data["pass"])):
                self.response['token'] = JWT.createJWT()
            else:
                return False
        except:
            return False



"""Схема доступа к ресурсу сервиса:
Пользователь запрашивает у Gate """
from django.shortcuts import render
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import hashlib
from . import models
from . import token

# Create your views here.
def get_json(request):
    if request.content_type == 'application/json':
        return json.loads(request.body)
    else:
        raise ValueError("request json - wrong!")
class JsonResponseRequestError(HttpResponse):
    def __init__(self):
        HttpResponse.__init__(self, "{'type': 'error', 'data': 'wrong request'}")

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
	            in cookie: token: "<RandomSignedToken>"
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
            self.token = token.SignedToken("This is Super Secret Key!!")
    '''
    def createUser(self):
        if self._request.method == "POST":
            jdata = json.loads(self._request.body)
            user = models.User()
            '''
    def isAuthorize(self):
        '''ПРоверка аторизованности выполнятеся с помощью  токена
        JWT:
        |       header = {"alg": "HS256", "typ": "JWT" }
        |       payload = {"login": "login"}
        |       token = base64(header).base64(payload)
            JWT = token.HMAC-SH256(token, secret_key)
        '''
        try:
            if self.token.random_token_test(self.data['token']):
                user_sess = models.UserSession.objects.filter( token = self.data['token'].split('.'))
                if len(user_sess) == 0:
                    return False
                else:
                    return True
        except:
            return False

    def authorize(self):
        '''Функция проверяющая полномочия неизвествного пользователя по логину и паролю
        '''
        try:
            user = models.User.objects.filter(nikname = self.data['login'])
            if (len(user) == 1) and (user[0].password == hashlib.sha256(self.data["pass"])):
                self.response['token'] = self.token.createJWT()
            else:
                return False
        except:
            return False




@csrf_exempt
def singup(request):
    try:
        if request.method == 'POST':
            data = get_json(request)
            try:
                user = models.User()
                user.from_json(data)
                user.group = models.Group.objects.filter(name = 'user')[0]
                user.save()
            except:
                return JsonResponseRequestError()
        else:
            return JsonResponseRequestError()
    except:
        print("++ERROR++")
        return JsonResponseRequestError()

"""Схема доступа к ресурсу сервиса:
Пользователь запрашивает у Gate """
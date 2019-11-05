from django.shortcuts import render
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.db import IntegrityError
from django.core.paginator import Paginator
import hashlib
from . import models
from . import token

# Create your views here.


def get_json(request):
    if request.content_type == 'application/json':
        return json.loads(request.body)
    else:
        raise ValueError("request json - wrong!")
class JsonResponseRequestError(JsonResponse):
    def __init__(self, data = "wrong request"):
        HttpResponse.__init__(self, f"{{'type': 'error', 'data': '{data}'}}")

class JsonResponseEmptyResult(JsonResponse):
    def __init__(self):
        HttpResponse.__init__(self, "{'type': 'error', 'data': 'Empty query result'}")

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
    def __init__(self, request, tokenType = token.RandomToken):
        if request.method == 'POST':
            self.data = json.loads(request.body.decode('utf8'))
            self.response = {}
            self.token = token.TokenCreator("This is Super Secret Key!!")
            self.user = None
            print("*---- In authorize constructor")

    def createUser(self):
        self.user = models.User()
        print(self.data)
        print(type(self.data))
        self.user.from_dict(self.data)
        print(models.User.objects.filter(login=self.data['login']))
        self.user.save(force_insert=True)
        self.user_authorize(self.user)
        print("*---- createUser")
    def isAuthorize(self):
        '''ПРоверка аторизованности выполнятеся с помощью  токена
        JWT:
        |       header = {"alg": "HS256", "typ": "JWT" }
        |       payload = {"login": "login"}
        |       token = base64(header).base64(payload)
            JWT = token.HMAC-SH256(token, secret_key)
        '''
        try:
            tok = self.data['token'].split('.')
            print(tok)
            tok = token.RandomToken(tok[0], tok[1])
            print(tok)
            if self.token.random_token_test(tok):
                user_sess = models.UserSession.objects.filter( token = tok.value())
                if len(user_sess) == 0:
                    return False
                else:
                    print(user_sess[0].user)
                    self.user = user_sess[0].user
                    return True
            else:
                return False
        except:
            return False

    def authorize_from_request(self):
        '''Функция проверяющая полномочия неизвествного пользователя по логину и паролю
        '''
        try:
            user = models.User.objects.filter(login = self.data['login'])
            print(user)
            print(user[0].password)
            print(hashlib.sha256(self.data["pass"].encode('utf8')).hexdigest())
            if (len(user) == 1) and (user[0].password == hashlib.sha256(self.data["pass"].encode('utf8')).hexdigest()):
                self.user_authorize(user[0])
                return True
            else:
                print("*****")
                return False
        except Exception as exp:
            print(exp)
            return False

    def user_authorize(self, user):
        self.response['token'] = self.token.create_token(20)
        sess = models.UserSession(user=user, token=self.response['token'].value())
        sess.save()
"""
def check_permissions(request):
    '''
    Request:
      {
	    "token": <RandomTokenAuthorizeUser>,
	    "service": <ServiceUUID>,
	    "object": <ObjectUUID>,
	    "action_uuid": <read|create|edit>
      }
    Response:
    {
        "type:" "PermissionCheck"
        "result": "ok/"
    }

    '''
    if request.method == 'POST':
        auth = Authorize(request)
        if auth.isAuthorize():
            object = models.ServiceObject.objects.filter(object_type = auth.data['object'])[0]
            if (len(object) != 0) and (object.service.uuid == auth.data['service']):
                #проверка личных прав пользователя
                permissions = models.UserPermission.objects.filter(user = auth.user)
                ok = False
                for perm in permissions:
                    if perm.uuid ==  auth.data['action_uuid']:
                        ok = True
                        break
                if ok == True:





                #проверка прав про группе пользователей



    else:
        return JsonResponseRequestError()
"""

@csrf_exempt
def singin(request):
    if request.method == 'POST':
        auth = Authorize(request)
        if auth.authorize_from_request():
            auth_token = auth.response['token'].value() + '.' + auth.response['token'].signature()
            return JsonResponse({"type": "ok", "token": auth_token})
        else:
            return JsonResponseRequestError()


@csrf_exempt
def singup(request):
    try:
        if request.method == 'POST':
            auth = Authorize(request)
            auth.createUser()
            auth_token = auth.response['token'].value() + '.' + auth.response['token'].signature()
            return JsonResponse({"type": "ok", "data": "user add in db", "token": auth_token, "user_uuid": auth.user.uuid})
        else:
            return JsonResponseRequestError()
    except IntegrityError as exp:
        print(exp)
        return JsonResponseRequestError("user with this login already exists")
    except Exception as exp:
        print(exp)
        return JsonResponseRequestError()


@csrf_exempt
def get_list_users(request, page = -1, page_len = 10):
    if request.method == 'GET':
        res = []
        users = models.User.objects.all()
        if page > -1:
            if page_len > 0:
                paginator = Paginator(users, page_len)
                if page <= paginator.num_pages:
                    users = paginator.page(page)
                else:
                    return JsonResponseRequestError("wrong number page")
            else:
                return JsonResponseRequestError("wrong page length for pagination result")

        for u in users:
            res.append(u.to_dict())
        if len(res) == 0:
            return JsonResponseEmptyResult()
        answer = {'type': 'users_list', 'users': res}
        if page > -1:
            answer['type'] = "users_list_pagination"
            answer['page'] = page
            answer['num_pages'] = paginator.num_pages
        return JsonResponse(answer)
    else:
        return JsonResponseRequestError()

@csrf_exempt
def check_permission(request):
    if request.method == 'POST':
        try:
            auth = Authorize(request)
            if auth.isAuthorize():
                if auth.user.check_permission(auth.data['service'], auth.data['object'], auth.data['permission']):
                    return JsonResponse({"type": "ok", "data": "allowed"})
                else:
                    return JsonResponse({"type": "ok", "data": "forbidden"})
            else:
                return JsonResponseRequestError('must authorize')
        except:
            return JsonResponseRequestError()
"""Схема доступа к ресурсу сервиса:
"""




@csrf_exempt
def check_permission2(request):
    if request.method == 'POST':
        auth = Authorize(request)
        if auth.isAuthorize():
            if auth.user.check_permission(auth.data['service'], auth.data['object'], auth.data['permission']):
                return JsonResponse({"type": "ok", "data": "allowed"})
            else:
                return JsonResponse({"type": "ok", "data": "forbidden"})
        else:
            return JsonResponse({"type": "error", "data": "must have authorize"})
    return HttpResponse("Error")

@csrf_exempt
def get_user_info(request):
    if request.method == 'POST':
        auth = Authorize(request)
        if auth.isAuthorize():
            return JsonResponse(auth.user.to_dict())


#TODO при авторизации все время выдается новый токен. Исправить этот недостаток по ip
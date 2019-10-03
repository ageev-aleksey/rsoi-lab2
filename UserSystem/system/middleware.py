import hashlib
from django.http import HttpRequest
import copy

def my_session(get_response):
    def middleware(request):

        response = get_response(request)
        return response




class AuthorizeRequest (HttpRequest):
    def __init__(self, request):
        self = copy.deepcopy(request)


class A:
    def __init__(self, a):
        self.a = a
        self.b = 2*a*a
    def foo(self):
        return (self.a, self.b)

class B(A):
    def __init__(self, request):
        self.request = request
    def __getattribute__(self, item, *args, **kwargs):
        self.request.item(args, *kwargs)
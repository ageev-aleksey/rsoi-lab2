import hashlib
def my_session(get_response):
    def middleware(request):

        response = get_response(request)
        return response
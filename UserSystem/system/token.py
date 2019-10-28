import base64
import hashlib
import hmac
import string
import random

def createJWT(payload_data, secret_key):
    if type(payload_data) == dict:
        header = '{"alg": "HS256", "typ": "JWT"}'
        payload = str(payload_data)
        ptoken = base64.b64encode(header.encode('utf8')).decode('utf8') + "." + base64.b64encode(payload.encode('utf8')).decode('utf8')
        token = ptoken + "." + hmac.new(
            key=secret_key.encode('utf-8'),
            msg=ptoken.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()
        return token
    else:
        raise ValueError("Argument must have type a dict. Now type is a " +  str(type(payload_data)))

def testJWT(jwt_token, secret_key):
    if type(jwt_token) == str:
        ptokens = jwt_token.split('.');
        recompute_token = hmac.new(
            key=secret_key.encode('utf-8'),
            msg=(ptokens[0] + "." + ptokens[1]).encode('utf8'),
            digestmod=hashlib.sha256
            ).hexdigest()
        return recompute_token == ptokens[2]
    else:
        raise ValueError("Argument must have type a dict. Now type is a " +  str(type(jwt_token)))

class TokenCreator:
    '''
    JWT:
    |       header = {"alg": "HS256", "typ": "JWT" }
    |       payload = {"login": "login"}
    |       token = base64(header).base64(payload)
        JWT = token.HMAC-SH256(token, secret_key)
    '''
    def __init__(self, secret_key, hash = hashlib.sha256):
        self._secret = secret_key
        self._hash = hash
    def __calc_signature__(self, data):
        return hmac.new(
                        key=self._secret.encode('utf-8'),
                        msg=data.encode('utf-8'),
                        digestmod=self._hash
                        ).hexdigest()
    '''def create_jwt(self, payload_data):
        if type(payload_data) == dict:
            header = '{"alg": "HS256", "typ": "JWT"}'
            payload = str(payload_data)
            ptoken = base64.b64encode(header.encode('utf8')).decode('utf8') + "." + \
                     base64.b64encode(payload.encode('utf8')).decode('utf8')
            token = ptoken + "." + hmac.new(
                key= self.secret.encode('utf-8'),
                msg=ptoken.encode('utf-8'),
                digestmod=self.hash
            ).hexdigest()
            return token
        else:
            raise ValueError("Argument must have type a dict. Now type is a " + str(type(payload_data)))'''
    def create_token(self, length):
        ptoken = ''.join([random.choice(string.ascii_lowercase + string.ascii_uppercase +
                                       string.digits) for i in range(length)])
        return RandomToken(ptoken, self.__calc_signature__(ptoken))
    def jwt_test(self, token):
        pass
    def random_token_test(self, token):
        if isinstance(token, RandomToken):
            print("=====")
            print(token)
            if token.signature() == self.__calc_signature__(token.value()):
                print("TRUE")
            else:
                print("FALSE")
            return token.signature() == self.__calc_signature__(token.value())
        else:
            raise ValueError("Argument token maust have type a RandomToken. Now type is " + str(type(token)))
    def random_token_from_data(self, data):
        pass


class Token:
    def __init__(self):
        pass
    def signature(self):
        pass
    def value(self):
        pass

class RandomToken (Token):
    def __init__(self, value, signature):
        self._value = value
        self._signature = signature
    def signature(self):
        return self._signature
    def value(self):
        return self._value
    def __str__(self):
        return self._value + '.' + self._signature
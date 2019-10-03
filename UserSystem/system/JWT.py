import base64
import hashlib
import hmac

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

class JWT:
    def __init__(self, secret_key, hash = hashlib.sha256):
        self.secret = secret_key
        self.hash = hash
    def create(self, payload_data):
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
            raise ValueError("Argument must have type a dict. Now type is a " + str(type(payload_data)))
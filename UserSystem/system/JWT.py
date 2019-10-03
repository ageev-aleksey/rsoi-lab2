import base64
import hashlib
import hmac

def createJWT(payload_data, secret_key):
    header = '{"alg": "HS256", "typ": "JWT"}'
    payload = '{ "data": "' + payload_data + '"}'
    ptoken = base64.b64encode(header.encode('utf8')).decode('utf8') + "." + base64.b64encode(payload.encode('utf8')).decode('utf8')
    token = ptoken + "." + hmac.new(
        key=secret_key.encode('utf-8'),
        msg=ptoken.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()
    return token

def testJWT(jwt_token, secret_key):
    ptokens = jwt_token.split('.');
    recompute_token = hmac.new(
        key=secret_key.encode('utf-8'),
        msg=(ptokens[0] + "." + ptokens[1]).encode('utf8'),
        digestmod=hashlib.sha256
    ).hexdigest()
    return recompute_token == ptokens[2]
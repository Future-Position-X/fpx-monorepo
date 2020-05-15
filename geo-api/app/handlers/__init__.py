import gzip
import base64
def response(status_code, payload=None):
    resp = {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
            "Content-Encoding": "gzip",
            "Content-Type": 'application/json',
        },
    }
    if payload != None:
        resp.update(
            {
                "body": base64.b64encode(gzip.compress(bytes(payload, 'utf-8'))).decode('utf-8'),
                "isBase64Encoded": True,
            }
        )
    return resp

def response(status_code, payload=None):
    return {
        "statusCode": status_code,
        "body": payload
    }

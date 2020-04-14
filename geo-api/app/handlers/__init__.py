def response(status_code, payload):
    return {
        "statusCode": status_code,
        "body": payload
    }

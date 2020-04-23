

def ping(event, context):
    print(event)
    return {
        "statusCode": 200,
        "body": "pong"
    }
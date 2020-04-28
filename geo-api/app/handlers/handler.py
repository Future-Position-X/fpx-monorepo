from app.handlers import response


def ping(event, context):
    print(event)
    return response(200,"pong")

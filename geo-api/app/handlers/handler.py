from app.handlers import response


def health(event, context):
    print(event)
    return response(200,"healthy!")

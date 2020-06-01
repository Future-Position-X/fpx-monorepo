from app import app
from flask import request
import jwt
import os

def response(status_code, payload=None):
    response = app.response_class(
        response=payload,
        status=status_code,
        mimetype='application/json'
    )
    return response

def get_provider_uuid_from_request():
    provider_uuid = ""
    return provider_uuid

def auth():
    print(request.headers)
    authHeader = request.headers['authorization']
    if authHeader is None:
        return

    authParts = authHeader.split(' ')
    if len(authParts) != 2:
        return

    if authParts[0].lower() != 'bearer':
        return

    token = authParts[1]

    try:
        decoded = jwt.decode(
            token,
            os.environ.get('JWT_SECRET'),
            algorithms=['HS256'])
    except Exception as e:
        print(e)
        return
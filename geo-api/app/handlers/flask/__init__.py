from app import app
from flask import request
import jwt
import os
from flask_jwt_extended import get_jwt_claims

def response(status_code, payload=None):
    response = app.response_class(
        response=payload,
        status=status_code,
        mimetype='application/json'
    )
    return response

def get_provider_uuid_from_request():
    claims = get_jwt_claims()
    print(claims)
    return claims['provider_uuid']
from app import app
from flask_jwt_extended import get_raw_jwt
from uuid import UUID

def handle_model_not_found_error(e):
    return {'error': 'not found'}, 404

def response(status_code, payload=None):
    response = app.response_class(
        response=payload,
        status=status_code,
        mimetype='application/json'
    )
    return response

def get_provider_uuid_from_request():
    claims = get_raw_jwt()
    return UUID(claims['provider_uuid'])
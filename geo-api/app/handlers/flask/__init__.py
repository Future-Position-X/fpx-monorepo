from app import app
from flask_jwt_extended import get_raw_jwt, get_jwt_identity
from uuid import UUID
from app.dto import InternalUserDTO


def handle_model_not_found_error(e):
    return {"error": "not found"}, 404


def response(status_code, payload=None):
    response = app.response_class(
        response=payload, status=status_code, mimetype="application/json"
    )
    return response


def get_provider_uuid_from_request():
    claims = get_raw_jwt()
    return UUID(claims.get("provider_uuid", "00000000-0000-0000-0000-000000000000"))


def get_user_uuid_from_request():
    return get_jwt_identity()


def get_user_from_request() -> InternalUserDTO:
    return InternalUserDTO(
        **{
            "uuid": get_user_uuid_from_request(),
            "provider_uuid": get_provider_uuid_from_request(),
        }
    )

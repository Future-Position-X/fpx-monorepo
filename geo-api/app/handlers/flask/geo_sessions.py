import rapidjson
import base64
from rapidjson import DM_ISO8601

from app import app
from app.handlers.flask import (
    response
)
from app.services.user import get_user_by_email
from app.services.session import (
    authenticate,
    create_access_token
    )
from flask import request
from flask_jwt_extended import jwt_required


@app.route('/sessions', methods=['POST'])
def sessions_create():
    json = request.json
    email = json["email"]
    password = json["password"]
    user = get_user_by_email(email)

    if authenticate(user, password):
        token = create_access_token(user.uuid, user.provider_uuid)
        return response(201, token)
    
    return response(401)
import rapidjson
import base64
from rapidjson import DM_ISO8601

from app import app, api
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
from flask_restx import Resource, fields

ns = api.namespace('sessions', 'Session operations', path="/")

from app.models import User as UserDB

@ns.route('/sessions')
class Session(Resource):
    def post(self):
        json = request.get_json()
        print("###########################")
        print(json)
        email = json["email"]
        password = json["password"]
        user = UserDB.first_or_fail(email=email)
    
        if authenticate(user, password):
            token = create_access_token(user.uuid, user.provider_uuid)
            return str(token), 201
        
        return '', 401
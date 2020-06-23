from app import api
from app.services.session import (
    authenticate,
    create_access_token
)
from flask import request
from flask_restx import Resource, fields

ns = api.namespace('sessions', 'Session operations', path="/")

from app.models import User as UserDB


@ns.route('/sessions')
class Session(Resource):
    @ns.doc(security=None)
    def post(self):
        json = request.get_json()
        email = json["email"]
        password = json["password"]
        user = UserDB.first_or_fail(email=email)

        try:
            if authenticate(user, password):
                token = create_access_token(user.uuid, user.provider_uuid)
                return {
                           'token': str(token)
                       }, 201
            else:
                return '', 401
        except ValueError:
            return '', 401

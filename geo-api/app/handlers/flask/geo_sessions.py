from flask import request
from flask_restx import Resource

from app import api
from app.services.session import (
    create_session
)

ns = api.namespace('sessions', 'Session operations', path="/")


@ns.route('/sessions')
class Session(Resource):
    @ns.doc(security=None)
    def post(self):
        json = request.get_json()
        email = json["email"]
        password = json["password"]
        try:
            token = create_session(email, password)
            return {
                       'token': token
                   }, 201
        except ValueError:
            return '', 401

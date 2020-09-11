from flask import request
from flask_restx import Resource, fields

from app import api
from app.services.session import create_session

ns = api.namespace("sessions", "Session operations", path="/")

create_session_model = api.model(
    "CreateSession",
    {
        "email": fields.String(description="email"),
        "password": fields.String(description="password"),
    },
)

token_model = api.model("Token", {"token": fields.String(description="token")})


@ns.route("/sessions")
class Session(Resource):
    @ns.doc(security=None)
    @ns.expect(create_session_model)
    @ns.marshal_with(token_model, code=201)
    def post(self):
        json = request.get_json()
        email = json["email"]
        password = json["password"]
        try:
            token = create_session(email, password)
            response = {"token": token}
            return response, 201
        except ValueError:
            return None, 401

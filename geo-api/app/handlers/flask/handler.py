from app import api
from app.handlers.flask import (
    response,
)
from flask_restx import Resource

ns = api.namespace('health', 'Api health check')


@ns.route('/')
class Health(Resource):
    def get(self):
        return "healthy!", 200

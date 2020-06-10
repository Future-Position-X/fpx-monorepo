import bcrypt
import rapidjson
import base64
from rapidjson import DM_ISO8601

from flask_restx import Resource, fields

from app import app, api
from app.models.user import User
from app.handlers.flask import (
    response
)
from app.services.user import (
    create_user,
    get_user_by_uuid,
    update_user_by_uuid,
    delete_user_by_uuid
    )
from flask import request
from flask_jwt_extended import jwt_required

ns = api.namespace('users', 'User operations')

from app.models import User as UserDB
from app.models import Provider as ProviderDB

user_model = api.model('User', {
    'uuid': fields.String(description='uuid'),
    'provider_uuid': fields.String(description='provider_uuid'),
    'email': fields.String(description='email'),
    'revision': fields.String(description='revision'),
    'created_at': fields.String(description='created_at'),
    'updated_at': fields.String(description='updated_at'),
})

create_user_model = api.model('User', {
    'email': fields.String(description='email'),
    'password': fields.String(description='password')
})

@ns.route('/')
class UserList(Resource):
    @jwt_required
    @ns.doc('create_user')
    @ns.expect(create_user_model)
    @ns.marshal_with(user_model, 201)
    def post(self):
        user = User(**request.get_json())
        user.password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        provider = ProviderDB.create(name=user.email)
        user.provider_uuid = provider.uuid
        user = UserDB.create(**user.as_dict())
        user.session().commit()
        return user, 201



# @app.route('/users/<user_uuid>')
# @jwt_required
# def users_get(user_uuid):
#     user = get_user_by_uuid(user_uuid)
#     return response(200, rapidjson.dumps(user.as_dict(), datetime_mode=DM_ISO8601))

# @app.route('/users', methods=['POST'])
# @jwt_required
# def users_create():
#     user = User(**request.json)
#     uuid = create_user(user)

#     return response(201, str(uuid))


# @app.route('/users/<user_uuid>', methods=['PUT'])
# @jwt_required
# def users_update(user_uuid):
#     user = User(**request.json)
#     update_user_by_uuid(user_uuid, user)

#     return response(204)


# @app.route('/users/<user_uuid>', methods=['DELETE'])
# @jwt_required
# def users_delete(user_uuid):
#     delete_user_by_uuid(user_uuid)
#     return response(204)
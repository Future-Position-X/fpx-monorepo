import bcrypt
from flask_restx import Resource, fields

from app import api
from app.models.user import User
from app.handlers.flask import (
    get_provider_uuid_from_request
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

create_user_model = api.model('CreateUser', {
    'email': fields.String(description='email'),
    'password': fields.String(description='password')
})

update_user_model = api.model('UpdateUser', {
    'password': fields.String(description='password')
})


@ns.route('/')
class UserList(Resource):
    @ns.doc('list_users', security=None)
    @ns.marshal_list_with(user_model)
    def get(self):
        user = UserDB.all()
        return user

    @ns.doc('create_user', security=None)
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


@ns.route('/<uuid:user_uuid>')
@ns.response(404, 'User not found')
@ns.param('user_uuid', 'The user identifier')
class UserApi(Resource):
    @ns.doc('get_user', security=None)
    @ns.marshal_with(user_model)
    def get(self, user_uuid):
        user = UserDB.find_or_fail(user_uuid)
        return user

    @jwt_required
    @ns.doc('update_user')
    @ns.expect(update_user_model)
    def put(self, user_uuid):
        provider_uuid = get_provider_uuid_from_request()
        user_dict = request.get_json()
        user_new = User(**user_dict)
        user = UserDB.first_or_fail(provider_uuid=provider_uuid, uuid=user_uuid)
        user.password = bcrypt.hashpw(user_new.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        user.save()
        user.session().commit()
        return '', 204

    @jwt_required
    @ns.doc('delete_user')
    def delete(self, user_uuid):
        provider_uuid = get_provider_uuid_from_request()
        user = UserDB.first_or_fail(provider_uuid=provider_uuid, uuid=user_uuid)
        user.delete()
        user.session().commit()
        return '', 204

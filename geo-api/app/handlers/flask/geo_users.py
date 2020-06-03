import rapidjson
import base64
from rapidjson import DM_ISO8601

from app import app
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


@app.route('/users/<user_uuid>')
@jwt_required
def users_get(user_uuid):
    user = get_user_by_uuid(user_uuid)
    return response(200, rapidjson.dumps(user.as_dict(), datetime_mode=DM_ISO8601))

@app.route('/users', methods=['POST'])
@jwt_required
def users_create():
    user = User(**request.json)
    uuid = create_user(user)

    return response(201, str(uuid))


@app.route('/users/<user_uuid>', methods=['PUT'])
@jwt_required
def users_update(user_uuid):
    user = User(**request.json)
    update_user_by_uuid(user_uuid, user)

    return response(204)


@app.route('/users/<user_uuid>', methods=['DELETE'])
@jwt_required
def users_delete(user_uuid):
    delete_user_by_uuid(user_uuid)
    return response(204)
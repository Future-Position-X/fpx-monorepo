import rapidjson
import base64
from rapidjson import DM_ISO8601

from app.models.user import User
from app.handlers import response
from app.services.user import (
    create_user,
    get_user_by_uuid,
    update_user_by_uuid,
    delete_user_by_uuid
    )


def get(event, context):
    user_uuid = event['pathParameters']['user_uuid']
    user = get_user_by_uuid(user_uuid)
    return response(200, rapidjson.dumps(user.as_dict(), datetime_mode=DM_ISO8601))


def create(event, context):
    payload = base64.b64decode(
        event['body']) if event['isBase64Encoded'] else event['body']
    json = rapidjson.loads(payload)
    user = User(**json)
    uuid = create_user(user)

    return response(201, str(uuid))


def update(event, context):
    user_uuid = event['pathParameters']['user_uuid']
    payload = base64.b64decode(
        event['body']) if event['isBase64Encoded'] else event['body']
    json = rapidjson.loads(payload)
    user = User(**json)
    update_user_by_uuid(user_uuid, user)

    return response(204)


def delete(event, context):
    user_uuid = event['pathParameters']['user_uuid']
    delete_user_by_uuid(user_uuid)
    return response(204)
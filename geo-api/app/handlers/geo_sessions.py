import rapidjson
import base64
from rapidjson import DM_ISO8601

from app.handlers import response
from app.services.user import get_user_by_email
from app.services.session import (
    authenticate,
    create_access_token
    )


def create(event, context):
    payload = base64.b64decode(
        event['body']) if event['isBase64Encoded'] else event['body']
    json = rapidjson.loads(payload)
    email = json["email"]
    password = json["password"]
    user = get_user_by_email(email)

    if authenticate(user, password):
        token = create_access_token(user.uuid, user.provider_uuid)
        return response(201, token)
    
    return response(401)
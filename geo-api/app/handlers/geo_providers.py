import rapidjson
import base64
from rapidjson import DM_ISO8601

from app.models.provider import Provider
from app.handlers import response
from app.services.provider import (
    get_provider_by_uuid,
    get_all_providers,
    update_provider_by_uuid,
    )


def index(event, context):
    providers = get_all_providers()

    return response(200, rapidjson.dumps([p.as_dict() for p in providers], datetime_mode=DM_ISO8601))


def get(event, context):
    provider_uuid = event['pathParameters']['provider_uuid']
    provider = get_provider_by_uuid(provider_uuid)
    return response(200, rapidjson.dumps(provider.as_dict(), datetime_mode=DM_ISO8601))


def update(event, context):
    provider_uuid = event['pathParameters']['provider_uuid']
    payload = base64.b64decode(
        event['body']) if event['isBase64Encoded'] else event['body']
    provider_dict = rapidjson.loads(payload)
    provider = Provider(**provider_dict)
    update_provider_by_uuid(provider_uuid, provider)
    return response(204)

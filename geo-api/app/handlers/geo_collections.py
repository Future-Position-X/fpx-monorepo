import rapidjson
import base64
from rapidjson import DM_ISO8601

from app.models.collection import Collection
from app.handlers import response
from app.services.collection import (
    get_all_collections, 
    create_collection,
    delete_collection_by_uuid,
    update_collection_by_uuid,
    get_collection_by_uuid
    )


def index(event, context):
    collections = get_all_collections()

    return response(200, rapidjson.dumps([c.as_dict() for c in collections], datetime_mode=DM_ISO8601))


def get(event, context):
    collection_uuid = event['pathParameters']['collection_uuid']
    collection = get_collection_by_uuid(collection_uuid)
    return response(200, rapidjson.dumps(collection.as_dict(), datetime_mode=DM_ISO8601))


def delete(event, context):
    collection_uuid = event['pathParameters']['collection_uuid']
    delete_collection_by_uuid(collection_uuid)
    return response(204)


def update(event, context):
    collection_uuid = event['pathParameters']['collection_uuid']
    payload = base64.b64decode(
        event['body']) if event['isBase64Encoded'] else event['body']
    collection_dict = rapidjson.loads(payload)
    collection = Collection(**collection_dict)
    update_collection_by_uuid(collection_uuid, collection)
    return response(204)


def create(event, context):
    provider_uuid = "99aaeecb-ccb0-4342-9704-3dfa49d66174"
    payload = base64.b64decode(
        event['body']) if event['isBase64Encoded'] else event['body']
    collection = rapidjson.loads(payload)
    collection['provider_uuid'] = provider_uuid
    collection = Collection(**collection)
    uuid = create_collection(collection)

    return response(201, uuid)

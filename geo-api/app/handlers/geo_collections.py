import rapidjson
from rapidjson import DM_ISO8601

from app.models.collection import Collection
from app.handlers import response
from app.services.collection import (
    get_all_collections, 
    delete_collection_by_uuid,
    update_collection_by_uuid,
    )


def index(event, context):
    collections = get_all_collections()

    return response(200, rapidjson.dumps([c.as_dict() for c in collections], datetime_mode=DM_ISO8601))


def delete(event, context):
    collection_uuid = event['pathParameters']['collection_uuid']
    delete_collection_by_uuid(collection_uuid)
    return response(204)


def update(event, context):
    collection_uuid = event['pathParameters']['collection_uuid']
    collection_dict = rapidjson.loads(event['body'])
    collection = Collection(**collection_dict)
    update_collection_by_uuid(collection_uuid, collection)
    return response(204)
import rapidjson
from rapidjson import DM_ISO8601

from app.models.item import Item

from app.services.item import (
    get_items_by_collection_uuid,
    create_item,
    create_items_by_collection_name_from_feature_collection)


def index(event, context):
    collection_uuid = event['pathParameters']['collection_uuid_or_name']
    items = get_items_by_collection_uuid(collection_uuid)

    response = {
        "statusCode": 200,
        "body": rapidjson.dumps([i.as_dict() for i in items], datetime_mode=DM_ISO8601)
    }
    return response


def create(event, context):
    payload = event['body']
    item_hash = rapidjson.loads(payload)
    item = Item(**item_hash)
    uuid = create_item(item)
    response = {
        "statusCode": 201,
        "body": uuid
    }
    return response


def create_by_collection_name_and_feature_collection(event, context):
    provider_uuid = "99aaeecb-ccb0-4342-9704-3dfa49d66174"
    collection_name = event['pathParameters']['collection_uuid_or_name']
    payload = event['body']
    feature_collection = rapidjson.loads(payload)

    uuids = create_items_by_collection_name_from_feature_collection(
        feature_collection=feature_collection,
        collection_name=collection_name,
        provider_uuid=provider_uuid)
    print(uuids)

    response = {
        "statusCode": 201,
        "body": rapidjson.dumps(uuids)
    }

    return response

import os
import rapidjson
from rapidjson import DM_ISO8601

from app.stores.item import ItemStore
from app.stores.collection import CollectionStore
from app.stores.base_store import StoreException
from app.models.item import Item

def index(event, context):
    collection_uuid = event['pathParameters']['collection_uuid']

    with ItemStore() as item_store:
        records = [c.as_dict()
                for c in item_store.find_by_collection_uuid(collection_uuid)]
        item_store.complete()
        response = {
            "statusCode": 200,
            "body": rapidjson.dumps(records, datetime_mode=DM_ISO8601)
        }

        return response

def create(event, context):
    payload = event['body']
    item_hash = rapidjson.loads(payload)
    item = Item(**item_hash)
    
    with ItemStore() as item_store:
        uuid = item_store.insert_one(item)
        item_store.complete()
        response = {
            "statusCode": 201,
            "body": uuid
        }

        return response

def get_collection_uuid_by_collection_name(collection_name):
    with CollectionStore() as collection_store:
        uuid = collection_store.get_uuid_by_name(collection_name)
        collection_store.complete()
        return uuid

def create_by_collection_name_and_feature_collection(event, context):
    provider_uuid = "99aaeecb-ccb0-4342-9704-3dfa49d66174"
    collection_name = event['pathParameters']['collection_name']
    collection_uuid = get_collection_uuid_by_collection_name(collection_name)
    payload = event['body']
    feature_collection = rapidjson.loads(payload)
    items = [
        Item(**{
            'provider_uuid': provider_uuid,
            'collection_uuid': collection_uuid,
            'geometry': feature['geometry'],
            'properties': feature['properties']
        }) for feature in feature_collection['features']]

    with ItemStore() as item_store:
        uuids = item_store.insert(items)
        print(uuids)
        item_store.complete()
        response = {
            "statusCode": 201,
            "body": rapidjson.dumps(uuids)
        }

        return response

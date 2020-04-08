import os
import rapidjson
from rapidjson import DM_ISO8601

from app.stores.collection import CollectionStore
from app.stores.base_store import StoreException


def index(event, context):
    with CollectionStore() as collection_store:
        records = [c.as_dict() for c in collection_store.find_all()]
        collection_store.complete()
        response = {
            "statusCode": 200,
            "body": rapidjson.dumps(records, datetime_mode=DM_ISO8601)
        }

        return response
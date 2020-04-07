import os
import rapidjson
from rapidjson import DM_ISO8601

from app.stores.item import ItemStore
from app.stores.base_store import StoreException

def index(event, context):
    try:
        with ItemStore() as item_store:
            records = [c.as_dict() for c in item_store.find_all()]
            item_store.complete()
            response = {
                "statusCode": 200,
                "body": rapidjson.dumps(records, datetime_mode=DM_ISO8601)
            }

            return response
    except StoreException as e:
        print(e)

import os
import rapidjson
from rapidjson import DM_ISO8601
from .. import db


def index(event, context):
    try:
        with db.CollectionStore() as collection_store:
            records = collection_store.find_all()
            collection_store.complete()
            response = {
                "statusCode": 200,
                "body": rapidjson.dumps(records, datetime_mode=DM_ISO8601)
            }
            print(response)
            return response
    except db.StoreException as e:
        print(e)

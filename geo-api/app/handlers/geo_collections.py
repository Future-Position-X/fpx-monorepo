import os
import rapidjson
from rapidjson import DM_ISO8601

from app.services.collection import get_all_collections

def index(event, context):
    collections = get_all_collections()
    response = {
        "statusCode": 200,
        "body": rapidjson.dumps([c.as_dict() for c in collections], datetime_mode=DM_ISO8601)
    }

    return response
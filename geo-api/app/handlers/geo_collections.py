import rapidjson
from rapidjson import DM_ISO8601

from app.handlers import response
from app.services.collection import get_all_collections


def index(event, context):
    collections = get_all_collections()

    return response(200, rapidjson.dumps([c.as_dict() for c in collections], datetime_mode=DM_ISO8601))

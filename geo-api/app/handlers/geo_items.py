import rapidjson
from rapidjson import DM_ISO8601
from uuid import UUID
from shapely.geometry import Point
from app.handlers import response
from app.models.item import Item

from app.services.collection import (
    get_collection_uuid_by_collection_name
)
from app.services.item import (
    get_items_by_collection_uuid,
    get_items_by_collection_uuid_as_geojson,
    get_items_within_radius_as_geojson,
    get_item_by_uuid_as_geojson,
    create_item,
    delete_item,
    create_items_from_geojson)


def get_collection_uuid_from_event(event):
    collection_uuid_or_name = event['pathParameters']['collection_uuid_or_name']
    try:
        return str(UUID(collection_uuid_or_name, version=4))
    except ValueError:
        return get_collection_uuid_by_collection_name(collection_uuid_or_name)


def get_limit_and_offset_from_event(event):
    print(event)
    offset = 0 if not event['queryStringParameters'].get('offset') else event['queryStringParameters']['offset']
    limit = 20 if not event['queryStringParameters'].get('limit') else event['queryStringParameters']['limit']
    return {
        "offset": offset,
        "limit": limit,
    }


def index(event, context):
    collection_uuid = get_collection_uuid_from_event(event)
    limit_offset = get_limit_and_offset_from_event(event)
    items = get_items_by_collection_uuid(collection_uuid, limit_offset)

    return response(200, rapidjson.dumps([i.as_dict() for i in items], datetime_mode=DM_ISO8601))


def get_within_radius(event, context):
    coordinates = event["queryStringParameters"]["coordinates"]
    lng, lat = coordinates.split(",")
    point_radius = {
        "point": Point(float(lng), float(lat)),
        "radius": float(event["queryStringParameters"]["radius"])
    }
    limit_offset = get_limit_and_offset_from_event(event)
    items = get_items_within_radius_as_geojson(point_radius, limit_offset)

    return response(200, rapidjson.dumps(items))


def get_as_geojson(event, context):
    item_uuid = event['pathParameters']['item_uuid']
    item = get_item_by_uuid_as_geojson(item_uuid)

    return response(200, rapidjson.dumps(item))


def index_as_geojson(event, context):
    collection_uuid = get_collection_uuid_from_event(event)
    limit_offset = get_limit_and_offset_from_event(event)
    geojson = get_items_by_collection_uuid_as_geojson(
        collection_uuid, limit_offset)

    return response(200, rapidjson.dumps(geojson))


def create(event, context):
    payload = event['body']
    item_hash = rapidjson.loads(payload)
    item = Item(**item_hash)
    uuid = create_item(item)

    return response(201, uuid)


def delete(event, context):
    item_uuid = event['pathParameters']['item_uuid']
    delete_item(item_uuid)
    return response(204)


def create_from_geojson(event, context):
    provider_uuid = "99aaeecb-ccb0-4342-9704-3dfa49d66174"
    collection_uuid = get_collection_uuid_from_event(event)
    payload = event['body']
    geojson = rapidjson.loads(payload)

    uuids = create_items_from_geojson(
        geojson=geojson,
        collection_uuid=collection_uuid,
        provider_uuid=provider_uuid)
    print(uuids)

    return response(201, rapidjson.dumps(uuids))

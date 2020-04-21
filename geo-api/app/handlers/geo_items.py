import rapidjson
import base64
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
    get_items_by_collection_uuid_as_png,
    get_items_within_radius_as_geojson,
    get_item_by_uuid_as_geojson,
    get_item_by_uuid_as_png,
    create_item,
    delete_item,
    update_item,
    add_items_from_geojson,
    create_items_from_geojson
    )


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


def get_visualizer_params_from_event(event):
    width = 1280
    height = 1280
    map_id = 'dark-v10'

    if event['queryStringParameters'] is not None:
        width = int(event['queryStringParameters'].get('width', width))
        height = int(event['queryStringParameters'].get('height', height))
        map_id = event['queryStringParameters'].get('mapid', map_id)

    return {
        "width": width,
        "height": height,
        "map_id": map_id
    }


def get_filter_from_event(event):
    filter = None

    if event['queryStringParameters'] is not None:
        filter = event['queryStringParameters'].get('filter', None)

    return filter


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


def get_as_png(event, context):
    item_uuid = event['pathParameters']['item_uuid']
    params = get_visualizer_params_from_event(event)
    png_bytes = get_item_by_uuid_as_png(
        item_uuid, params['width'], params['height'], params['map_id'])

    return {
        "statusCode": 200,
        "body": base64.b64encode(png_bytes),
        "isBase64Encoded": "true",
        "headers": {
            "Content-Type": "image/png"
        }
    }


def index_as_geojson(event, context):
    collection_uuid = get_collection_uuid_from_event(event)
    limit_offset = get_limit_and_offset_from_event(event)
    filter = get_filter_from_event(event)
    geojson = get_items_by_collection_uuid_as_geojson(
        collection_uuid, filter, limit_offset)

    return response(200, rapidjson.dumps(geojson))


def index_as_png(event, context):
    collection_uuid = get_collection_uuid_from_event(event)
    limit_offset = get_limit_and_offset_from_event(event)
    params = get_visualizer_params_from_event(event)
    png_bytes = get_items_by_collection_uuid_as_png(
        collection_uuid, limit_offset, params['width'], params['height'], params['map_id'])

    return {
        "statusCode": 200,
        "body": base64.b64encode(png_bytes),
        "isBase64Encoded": "true",
        "headers": {
            "Content-Type": "image/png"
        }
    }


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


def update(event, context):
    item_uuid = event['pathParameters']['item_uuid']
    item_hash = rapidjson.loads(event['body'])
    item = Item(**item_hash)
    update_item(item_uuid, item)
    return response(204)


def add_from_geojson(event, context):
    provider_uuid = "99aaeecb-ccb0-4342-9704-3dfa49d66174"
    collection_uuid = get_collection_uuid_from_event(event)
    payload = event['body']
    geojson = rapidjson.loads(payload)

    uuids = add_items_from_geojson(
        geojson=geojson,
        collection_uuid=collection_uuid,
        provider_uuid=provider_uuid)

    return response(201, rapidjson.dumps(uuids))


def create_from_geojson(event, context):
    provider_uuid = "99aaeecb-ccb0-4342-9704-3dfa49d66174"
    collection_uuid = get_collection_uuid_from_event(event)
    payload = event['body']
    geojson = rapidjson.loads(payload)

    uuids = create_items_from_geojson(
        geojson=geojson,
        collection_uuid=collection_uuid,
        provider_uuid=provider_uuid)

    return response(201, rapidjson.dumps(uuids))

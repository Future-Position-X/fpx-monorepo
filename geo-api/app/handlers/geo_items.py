import rapidjson
import base64
from rapidjson import DM_ISO8601
from uuid import UUID
from shapely.geometry import Point
from app.handlers import response
from app.models.item import Item
from distutils.util import strtobool

from app.services.collection import (
    get_collection_uuid_by_collection_name
)
from app.services.item import (
    get_items_by_collection_uuid,
    get_items_by_collection_uuid_as_geojson,
    get_items_by_collection_uuid_as_png,
    get_items_by_collection_name,
    get_items_by_collection_name_as_geojson,
    get_items_by_collection_name_as_png,
    get_items_within_radius_as_geojson,
    get_item_by_uuid_as_geojson,
    get_item_by_uuid_as_png,
    create_item,
    delete_item,
    update_item,
    add_items_from_geojson,
    create_items_from_geojson,
    update_items_from_geojson,
    delete_items_by_collection_uuid
    )

from app.services.ai import (
    generate_paths_from_points
)


def get_collection_uuid_from_event(event):
    collection_uuid = event['pathParameters'].get('collection_uuid')
    return collection_uuid


def get_filters_from_event(event):
    offset = 0
    limit = 20
    property_filter = None
    valid = False

    params = event['queryStringParameters']

    if params is not None:
        offset = int(params.get('offset', offset))
        limit =  int(params.get('limit', limit))
        property_filter = params.get('property_filter', property_filter)
        valid = bool(strtobool(params.get('valid', 'false')))

    return {
        "offset": offset,
        "limit": limit,
        "property_filter": property_filter,
        "valid": valid
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


def index(event, context):
    collection_uuid = get_collection_uuid_from_event(event)
    filters = get_filters_from_event(event)
    items = get_items_by_collection_uuid(collection_uuid, filters)

    return response(200, rapidjson.dumps([i.as_dict() for i in items], datetime_mode=DM_ISO8601))


def index_by_name(event, context):
    collection_name = event['pathParameters']['collection_name']
    filters = get_filters_from_event(event)
    items = get_items_by_collection_name(collection_name, '99aaeecb-ccb0-4342-9704-3dfa49d66174', filters)

    return response(200, rapidjson.dumps([i.as_dict() for i in items]))

def get_within_radius(event, context):
    coordinates = event["queryStringParameters"]["coordinates"]
    lng, lat = coordinates.split(",")
    point_radius = {
        "point": Point(float(lng), float(lat)),
        "radius": float(event["queryStringParameters"]["radius"])
    }
    filters = get_filters_from_event(event)
    items = get_items_within_radius_as_geojson(point_radius, filters)

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
    filters = get_filters_from_event(event)
    geojson = get_items_by_collection_uuid_as_geojson(collection_uuid, filters)

    return response(200, rapidjson.dumps(geojson))


def index_as_geojson_by_name(event, context):
    collection_name = event['pathParameters']['collection_name']
    filters = get_filters_from_event(event)
    geojson = get_items_by_collection_name_as_geojson(collection_name, '99aaeecb-ccb0-4342-9704-3dfa49d66174', filters)

    return response(200, rapidjson.dumps(geojson))


def index_as_png(event, context):
    collection_uuid = get_collection_uuid_from_event(event)
    filters = get_filters_from_event(event)
    vis_params = get_visualizer_params_from_event(event)
    png_bytes = get_items_by_collection_uuid_as_png(
        collection_uuid, filters, vis_params['width'], vis_params['height'], vis_params['map_id'])

    return {
        "statusCode": 200,
        "body": base64.b64encode(png_bytes),
        "isBase64Encoded": "true",
        "headers": {
            "Content-Type": "image/png"
        }
    }


def index_as_png_by_name(event, context):
    collection_name = event['pathParameters']['collection_name']
    filters = get_filters_from_event(event)
    vis_params = get_visualizer_params_from_event(event)
    png_bytes = get_items_by_collection_name_as_png(
        collection_name, '99aaeecb-ccb0-4342-9704-3dfa49d66174', filters, vis_params['width'], vis_params['height'], vis_params['map_id'])

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

def generate_walking_paths(event, context):
    provider_uuid = "99aaeecb-ccb0-4342-9704-3dfa49d66174"
    collection_uuid = get_collection_uuid_from_event(event)
    filters = {
        "offset": 0,
        "limit": 1000,
        "property_filter": None,
        "valid": False
    }
    steps = min(int(event['queryStringParameters']['steps']), 200)
    n_agents = min(int(event['queryStringParameters']['agents']), 50) 
    starting_points_collection_uuid = event['queryStringParameters']['starting_points_collection_uuid']
    environment_collection_uuid = event['queryStringParameters']['environment_collection_uuid']
    uuids = generate_paths_from_points(
        starting_points_collection_uuid, 
        environment_collection_uuid, 
        collection_uuid,
        n_agents, 
        steps, 
        provider_uuid,
        filters
    )
    return response(201, rapidjson.dumps(uuids))

def add_from_geojson(event, context):
    # user_id = event['requestContext']['authorizer']['principalId']
    # Get provider_uuid from user_id
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
    # user_id = event['requestContext']['authorizer']['principalId']
    # Get provider_uuid from user_id
    provider_uuid = "99aaeecb-ccb0-4342-9704-3dfa49d66174"
    collection_uuid = get_collection_uuid_from_event(event)
    payload = event['body']
    geojson = rapidjson.loads(payload)

    uuids = create_items_from_geojson(
        geojson=geojson,
        collection_uuid=collection_uuid,
        provider_uuid=provider_uuid)

    return response(201, rapidjson.dumps(uuids))

 
def update_from_geojson(event, context):
    feature_collection = rapidjson.loads(event['body'])
    update_items_from_geojson(feature_collection)
    return response(204)


def delete_items(event, context):
    collection_uuid = get_collection_uuid_from_event(event)
    delete_items_by_collection_uuid(collection_uuid)
    return response(204)

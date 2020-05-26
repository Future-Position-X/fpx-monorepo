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
    generate_paths_from_points,
    get_sequence_for_sensor
)
from app.services.session import get_provider_uuid_from_event


def get_collection_uuid_from_event(event):
    collection_uuid = event['pathParameters'].get('collection_uuid')
    return collection_uuid


def valid_envelope(params):
    if 'spatial_filter.envelope.ymin' in params and 'spatial_filter.envelope.xmin' in params and 'spatial_filter.envelope.ymax' in params and 'spatial_filter.envelope.xmax' in params:
        return True
    return False


def valid_distance(params):
    if 'spatial_filter.distance.x' in params and 'spatial_filter.distance.y' in params and 'spatial_filter.distance.d' in params:
        return True
    return False


def get_spatial_filter(params):
    if not params.get('spatial_filter'):
        return None
    else:
        if params.get('spatial_filter') == "within-distance":
            if not valid_distance(params):
                return None
            else:
                return {
                    'filter': params.get('spatial_filter'),
                    'distance': {
                        'point': Point(float(params.get('spatial_filter.distance.x')), float(params.get('spatial_filter.distance.y'))),
                        'd': float(params.get('spatial_filter.distance.d')),
                    }
                }
        elif params.get('spatial_filter') in ['within', 'intersect'] and valid_envelope(params):
            return {
                'filter': params.get('spatial_filter'),
                'envelope': {
                    'ymin': float(params.get('spatial_filter.envelope.ymin')),
                    'xmin': float(params.get('spatial_filter.envelope.xmin')),
                    'ymax': float(params.get('spatial_filter.envelope.ymax')),
                    'xmax': float(params.get('spatial_filter.envelope.xmax'))
                }
            }
        else:
            None

def get_transforms_from_event(event):
    simplify = 0.0
    params = event['queryStringParameters']

    if params is not None:
        simplify = float(params.get('simplify', simplify))

    return {
        "simplify": simplify,
    }

def get_filters_from_event(event):
    offset = 0
    limit = 20
    property_filter = None
    valid = False
    spatial_filter = None

    params = event['queryStringParameters']

    if params is not None:
        offset = int(params.get('offset', offset))
        limit = int(params.get('limit', limit))
        property_filter = params.get('property_filter', property_filter)
        valid = bool(strtobool(params.get('valid', 'false')))
        spatial_filter = get_spatial_filter(params)

    return {
        "offset": offset,
        "limit": limit,
        "property_filter": property_filter,
        "valid": valid,
        "spatial_filter": spatial_filter,
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


def get_format_from_event(event):
    format = "geojson"

    if event['queryStringParameters'] is not None:
        format = event['queryStringParameters'].get('format', format)
    
    return format


def index(event, context):
    collection_uuid = get_collection_uuid_from_event(event)
    filters = get_filters_from_event(event)
    transforms = get_transforms_from_event(event)
    format = get_format_from_event(event)

    if format == "json":
        items = get_items_by_collection_uuid(collection_uuid, filters)
        return response(200, rapidjson.dumps([i.as_dict() for i in items], datetime_mode=DM_ISO8601))
    elif format == "geojson":
        items = get_items_by_collection_uuid_as_geojson(collection_uuid, filters, transforms)
        return response(200, rapidjson.dumps(items))
    elif format == "png":
        vis_params = get_visualizer_params_from_event(event)
        png_bytes = get_items_by_collection_uuid_as_png(
            collection_uuid, filters, vis_params['width'], vis_params['height'], vis_params['map_id'], transforms)

        return {
            "statusCode": 200,
            "body": base64.b64encode(png_bytes).decode('utf-8'),
            "isBase64Encoded": "true",
            "headers": {
                "Content-Type": "image/png"
            }
        }
    else:
        return response(400, "invalid format")


def index_by_name(event, context):
    collection_name = event['pathParameters']['collection_name']
    filters = get_filters_from_event(event)
    format = get_format_from_event(event)
    provider_uuid = get_provider_uuid_from_event(event)

    if format == "json":
        items = get_items_by_collection_name(collection_name, provider_uuid, filters)
        return response(200, rapidjson.dumps([i.as_dict() for i in items]))
    elif format == "geojson":
        items = get_items_by_collection_name_as_geojson(collection_name, provider_uuid, filters)
        return response(200, rapidjson.dumps(items))
    elif format == "png":
        vis_params = get_visualizer_params_from_event(event)
        png_bytes = get_items_by_collection_name_as_png(
            collection_name, provider_uuid, filters, vis_params['width'], vis_params['height'], vis_params['map_id'])

        return {
            "statusCode": 200,
            "body": base64.b64encode(png_bytes).decode('utf-8'),
            "isBase64Encoded": "true",
            "headers": {
                "Content-Type": "image/png"
            }
        }
    

def get(event, context):
    item_uuid = event['pathParameters']['item_uuid']
    format = get_format_from_event(event)

    if format == "json":
        # not implemented yet
        return response(501)
    elif format == "geojson":
        item = get_item_by_uuid_as_geojson(item_uuid)
        return response(200, rapidjson.dumps(item))
    elif format == "png":
        params = get_visualizer_params_from_event(event)
        png_bytes = get_item_by_uuid_as_png(
            item_uuid, params['width'], params['height'], params['map_id'])

        return {
            "statusCode": 200,
            "body": base64.b64encode(png_bytes).decode('utf-8'),
            "isBase64Encoded": "true",
            "headers": {
                "Content-Type": "image/png"
            }
        }
    else:
        return response(400, "invalid format")


def create(event, context):
    payload = base64.b64decode(
        event['body']) if event['isBase64Encoded'] else event['body']
    item_hash = rapidjson.loads(payload)
    item = Item(**item_hash)
    uuid = create_item(item)

    return response(201, uuid)


def create_from_geojson(event, context):
    # user_id = event['requestContext']['authorizer']['principalId']
    # Get provider_uuid from user_id
    provider_uuid = get_provider_uuid_from_event(event)
    collection_uuid = get_collection_uuid_from_event(event)
    payload = base64.b64decode(
        event['body']) if event['isBase64Encoded'] else event['body']
    geojson = rapidjson.loads(payload)

    uuids = create_items_from_geojson(
        geojson=geojson,
        collection_uuid=collection_uuid,
        provider_uuid=provider_uuid)

    return response(201, rapidjson.dumps(uuids))


def delete(event, context):
    item_uuid = event['pathParameters']['item_uuid']
    delete_item(item_uuid)
    return response(204)


def delete_items(event, context):
    collection_uuid = get_collection_uuid_from_event(event)
    delete_items_by_collection_uuid(collection_uuid)
    return response(204)


def update(event, context):
    item_uuid = event['pathParameters']['item_uuid']
    payload = base64.b64decode(
        event['body']) if event['isBase64Encoded'] else event['body']
    item_hash = rapidjson.loads(payload)
    item = Item(**item_hash)
    update_item(item_uuid, item)
    return response(204)

def update_from_geojson(event, context):
    payload = base64.b64decode(
        event['body']) if event['isBase64Encoded'] else event['body']
    feature_collection = rapidjson.loads(payload)
    update_items_from_geojson(feature_collection)
    return response(204)

def add_from_geojson(event, context):
    # user_id = event['requestContext']['authorizer']['principalId']
    # Get provider_uuid from user_id
    provider_uuid = get_provider_uuid_from_event(event)
    collection_uuid = get_collection_uuid_from_event(event)
    payload = base64.b64decode(
        event['body']) if event['isBase64Encoded'] else event['body']
    geojson = rapidjson.loads(payload)

    uuids = add_items_from_geojson(
        geojson=geojson,
        collection_uuid=collection_uuid,
        provider_uuid=provider_uuid)

    return response(201, rapidjson.dumps(uuids))

def generate_walking_paths(event, context):
    provider_uuid = get_provider_uuid_from_event(event)
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
    
def prediction_for_sensor_item(event, context):
    item_uuid = event['pathParameters']['item_uuid']
    filters = get_filters_from_event(event)
    start_date = event["queryStringParameters"]["startdate"]
    end_date = event["queryStringParameters"]["enddate"]
    sequence_data = get_sequence_for_sensor(item_uuid, filters, start_date, end_date)
    return response(200, sequence_data)

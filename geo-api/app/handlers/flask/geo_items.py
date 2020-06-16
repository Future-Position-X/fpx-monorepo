import rapidjson
import base64

import sqlalchemy_mixins
from rapidjson import DM_ISO8601, UM_CANONICAL

from shapely.geometry import Point
from sqlalchemy import or_

from app.models.item import Item
from app.models import Item as ItemDB
from app.models import Collection as CollectionDB
from distutils.util import strtobool
from app import app, api, db
from app.handlers.flask import (
    response,
    get_provider_uuid_from_request,

)
from flask import request
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

from lib.visualizer.renderer import render_feature_collection, render_feature

from app.services.ai import (
    generate_paths_from_points,
    get_sequence_for_sensor
)

from flask_jwt_extended import jwt_required
from flask_restx import Resource, fields
from flask_accept import accept, accept_fallback
import flask

from geoalchemy2.shape import to_shape
from shapely.geometry import mapping
from shapely_geojson import dumps, Feature, FeatureCollection


class GeometryFormatter(fields.Raw):
    def format(self, value):
        return mapping(to_shape(value))


item_model = api.model('Item', {
    'uuid': fields.String(description='uuid'),
    'provider_uuid': fields.String(description='provider_uuid'),
    'collection_uuid': fields.String(description='collection_uuid'),
    'geometry': GeometryFormatter(),
    'properties': fields.Raw(description='properties'),
    'revision': fields.String(description='revision'),
    'created_at': fields.String(description='created_at'),
    'updated_at': fields.String(description='updated_at'),
})

create_item_model = api.model('Item', {
    'geometry': GeometryFormatter(),
    'properties': fields.Wildcard(fields.String, description='properties'),
})

update_item_model = api.model('Item', {
    'geometry': GeometryFormatter(),
    'properties': fields.Wildcard(fields.String, description='properties'),
})

bulk_create_item_response_model = api.model('Item', {
    'uuid': fields.String(description='uuid'),
})


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
                        'point': Point(float(params.get('spatial_filter.distance.x')),
                                       float(params.get('spatial_filter.distance.y'))),
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


def get_transforms_from_request():
    simplify = 0.0
    params = request.args

    if params is not None:
        simplify = float(params.get('simplify', simplify))

    return {
        "simplify": simplify,
    }


def get_filters_from_request():
    offset = 0
    limit = 20
    property_filter = None
    valid = False
    spatial_filter = None
    params = request.args

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


def get_visualizer_params_from_request():
    width = int(request.args.get('width', 1280))
    height = int(request.args.get('height', 1280))
    map_id = request.args.get('map_id', 'dark-v10')

    return {
        "width": width,
        "height": height,
        "map_id": map_id
    }


def get_format_from_request():
    format = request.args.get('format', "geojson")
    return format


ns = api.namespace('items', description='Item operations', path='/')

from shapely.geometry.collection import GeometryCollection


@ns.route('/collections/<uuid:collection_uuid>/items')
class CollectionItemList(Resource):
    @accept_fallback
    @jwt_required
    @ns.doc('list_collection_items')
    @ns.marshal_list_with(item_model)
    def get(self, collection_uuid):
        provider_uuid = get_provider_uuid_from_request()
        filters = get_filters_from_request()
        items = ItemDB.find_by_collection_uuid(provider_uuid, collection_uuid, filters)
        return items

    @get.support('application/geojson')
    @jwt_required
    @ns.doc('list_collection_items')
    def get_geojson(self, collection_uuid):
        provider_uuid = get_provider_uuid_from_request()
        filters = get_filters_from_request()
        transforms = get_transforms_from_request()
        items = ItemDB.find_by_collection_uuid_with_simplify(provider_uuid, collection_uuid, filters, transforms)
        features = [Feature(to_shape(item.geometry), item.properties) for item in items if item.geometry is not None]
        feature_collection = dumps(FeatureCollection(features))
        return flask.make_response(feature_collection, 200)

    @get.support('image/png')
    @jwt_required
    @ns.doc('list_collection_items')
    def get_png(self, collection_uuid):
        provider_uuid = get_provider_uuid_from_request()
        filters = get_filters_from_request()
        items = ItemDB.find_by_collection_uuid(provider_uuid, collection_uuid, filters)
        features = [Feature(to_shape(item.geometry), item.properties) for item in items]
        feature_collection = FeatureCollection(features).__geo_interface__
        params = get_visualizer_params_from_request()
        data = render_feature_collection(feature_collection, params['width'], params['height'], params['map_id'])
        return flask.make_response(data, 200, {'content-type': 'image/png'})

    @accept('application/json')
    @jwt_required
    @ns.doc('create_collection_item')
    @ns.expect(create_item_model)
    @ns.marshal_with(item_model, 201)
    def post(self, collection_uuid):
        provider_uuid = get_provider_uuid_from_request()
        coll = CollectionDB.first_or_fail(uuid=collection_uuid, provider_uuid=provider_uuid)
        item_hash = request.get_json()
        item_hash['collection_uuid'] = coll.uuid
        item = ItemDB(**item_hash)

        item.save()
        item.session().commit()
        return item, 201

    @post.support('application/geojson')
    @jwt_required
    @ns.doc('create_collection_item')
    @ns.expect(create_item_model)
    @ns.marshal_list_with(bulk_create_item_response_model, code=201)
    def post_geojson(self, collection_uuid):
        from shapely.geometry import shape
        provider_uuid = get_provider_uuid_from_request()
        coll = CollectionDB.first_or_fail(uuid=collection_uuid, provider_uuid=provider_uuid)
        geojson = request.get_json(force=True)

        ItemDB.where(collection_uuid=coll.uuid).delete()

        items = [
            ItemDB(**{
                'collection_uuid': coll.uuid,
                'geometry': shape(feature['geometry']).to_wkt(),
                'properties': feature['properties']
            }) for feature in geojson['features']]

        ItemDB.session().bulk_save_objects(items)
        ItemDB.session().commit()

        items = ItemDB.where(collection_uuid=coll.uuid).all()
        return items, 201

    @accept_fallback
    @jwt_required
    @ns.doc('delete_collection_items')
    def delete(self, collection_uuid):
        provider_uuid = get_provider_uuid_from_request()
        ItemDB.delete_by_collection_uuid(provider_uuid, collection_uuid)
        return '', 204

@ns.route('/collections/<uuid:collection_uuid>/items/<uuid:item_uuid>')
@ns.response(404, 'Item not found')
@ns.param('collection_uuid', 'The collection identifier')
@ns.param('item_uuid', 'The item identifier')
class CollectionItemApi(Resource):
    @accept_fallback
    @jwt_required
    @ns.doc('get_item')
    @ns.marshal_with(item_model)
    def get(self, collection_uuid, item_uuid):
        provider_uuid = get_provider_uuid_from_request()
        item = ItemDB.find_accessible_or_fail(provider_uuid, item_uuid, collection_uuid)
        return item

    @get.support('application/geojson')
    @jwt_required
    @ns.doc('get_item')
    def get_geojson(self, collection_uuid, item_uuid):
        provider_uuid = get_provider_uuid_from_request()
        item = ItemDB.find_accessible_or_fail(provider_uuid, item_uuid, collection_uuid)
        feature = Feature(to_shape(item.geometry), item.properties)
        return flask.make_response(dumps(feature), 200)

    @get.support('image/png')
    @jwt_required
    @ns.doc('get_item')
    def get_png(self, collection_uuid, item_uuid):
        provider_uuid = get_provider_uuid_from_request()
        item = ItemDB.find_accessible_or_fail(provider_uuid, item_uuid, collection_uuid)
        feature = Feature(to_shape(item.geometry), item.properties).__geo_interface__
        params = get_visualizer_params_from_request()
        data = render_feature(feature, params['width'], params['height'], params['map_id'])
        return flask.make_response(data, 200, {'content-type': 'image/png'})

    @accept_fallback
    @jwt_required
    @ns.doc('delete_item')
    def delete(self, collection_uuid, item_uuid):
        provider_uuid = get_provider_uuid_from_request()
        ItemDB.delete_owned(provider_uuid, item_uuid, collection_uuid)
        return '', 204


@ns.route('/collections/by_name/<collection_name>/items')
class CollectionByNameItemList(Resource):
    @accept_fallback
    @jwt_required
    @ns.doc('list_items_by_name')
    @ns.marshal_list_with(item_model)
    def get(self, collection_name):
        provider_uuid = get_provider_uuid_from_request()
        filters = get_filters_from_request()
        items = ItemDB.find_by_collection_name(provider_uuid, collection_name, filters)
        return items

    @get.support('application/geojson')
    @jwt_required
    @ns.doc('list_items_by_name')
    def get_geojson(self, collection_name):
        provider_uuid = get_provider_uuid_from_request()
        filters = get_filters_from_request()
        transforms = get_transforms_from_request()
        items = ItemDB.find_by_collection_name_with_simplify(provider_uuid, collection_name, filters, transforms)
        features = [Feature(to_shape(item.geometry), item.properties) for item in items if item.geometry is not None]
        feature_collection = dumps(FeatureCollection(features))
        return flask.make_response(feature_collection, 200)

    @get.support('image/png')
    @jwt_required
    @ns.doc('list_items_by_name')
    def get_png(self, collection_name):
        filters = get_filters_from_request()
        provider_uuid = get_provider_uuid_from_request()
        items = ItemDB.find_by_collection_name(provider_uuid, collection_name, filters)
        features = [Feature(to_shape(item.geometry), item.properties) for item in items]
        feature_collection = FeatureCollection(features).__geo_interface__
        params = get_visualizer_params_from_request()
        data = render_feature_collection(feature_collection, params['width'], params['height'], params['map_id'])
        return flask.make_response(data, 200, {'content-type': 'image/png'})


@ns.route('/items/<uuid:item_uuid>')
@ns.response(404, 'Item not found')
@ns.param('item_uuid', 'The item identifier')
class ItemApi(Resource):
    @accept_fallback
    @jwt_required
    @ns.doc('get_item')
    @ns.marshal_with(item_model)
    def get(self, item_uuid):
        provider_uuid = get_provider_uuid_from_request()
        item = ItemDB.find_accessible_or_fail(provider_uuid, item_uuid)
        return item

    @get.support('application/geojson')
    @jwt_required
    @ns.doc('get_item')
    def get_geojson(self, item_uuid):
        provider_uuid = get_provider_uuid_from_request()
        item = ItemDB.find_accessible_or_fail(provider_uuid, item_uuid)
        feature = Feature(to_shape(item.geometry), item.properties)
        return flask.make_response(dumps(feature), 200)

    @get.support('image/png')
    @jwt_required
    @ns.doc('get_item')
    def get_png(self, item_uuid):
        provider_uuid = get_provider_uuid_from_request()
        item = ItemDB.find_accessible_or_fail(provider_uuid, item_uuid)
        feature = Feature(to_shape(item.geometry), item.properties).__geo_interface__
        params = get_visualizer_params_from_request()
        data = render_feature(feature, params['width'], params['height'], params['map_id'])
        return flask.make_response(data, 200, {'content-type': 'image/png'})

    @accept_fallback
    @jwt_required
    @ns.doc('delete_item')
    def delete(self, item_uuid):
        provider_uuid = get_provider_uuid_from_request()
        ItemDB.delete_owned(provider_uuid, item_uuid)
        return '', 204

    @accept_fallback
    @jwt_required
    @ns.doc('update_item')
    @ns.expect(update_item_model)
    def put(self, item_uuid):
        provider_uuid = get_provider_uuid_from_request()
        item_dict = request.get_json(force=True)
        item_new = Item(**item_dict)

        item = ItemDB.find_accessible_or_fail(provider_uuid, item_uuid)

        item.properties = item_new.properties
        item.geometry = item_new.geometry

        item.save()
        item.session().commit()
        return '', 204

    @put.support('application/geojson')
    @jwt_required
    @ns.doc('update_item')
    @ns.marshal_list_with(bulk_create_item_response_model, code=201)
    def put_geojson(self, item_uuid):
        from shapely.geometry import shape
        provider_uuid = get_provider_uuid_from_request()
        geojson = request.get_json(force=True)
        feature = geojson['feature']
        item = ItemDB.find_owned_or_fail(provider_uuid, item_uuid)

        item_new = ItemDB(**{
                'geometry': shape(feature['geometry']).to_wkt(),
                'properties': feature['properties']
            })

        item.properties = item_new.properties
        item.geometry = item_new.geometry

        item.save
        item.session().commit()

        return '', 204


# @app.route('/items/geojson', methods=['PUT'])
@jwt_required
def update_from_geojson():
    feature_collection = request.json
    update_items_from_geojson(feature_collection)
    return response(204)


# @app.route('/collections/<collection_uuid>/items/geojson', methods=['PUT'])
@jwt_required
def add_from_geojson(collection_uuid):
    provider_uuid = get_provider_uuid_from_request()
    geojson = request.json

    uuids = add_items_from_geojson(
        geojson=geojson,
        collection_uuid=collection_uuid,
        provider_uuid=provider_uuid)

    return response(201, rapidjson.dumps(uuids))


# @app.route('/collections/<collection_uuid>/items/ai/generate/walkingpaths', methods=['POST'])
@jwt_required
def generate_walking_paths(collection_uuid):
    provider_uuid = get_provider_uuid_from_request()
    filters = {
        "offset": 0,
        "limit": 1000,
        "property_filter": None,
        "valid": False
    }
    steps = min(int(request.args.get('steps')), 200)
    n_agents = min(int(request.args.get('agents')), 50)
    starting_points_collection_uuid = request.args.get('starting_points_collection_uuid')
    environment_collection_uuid = request.args.get('environment_collection_uuid')
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


# @app.route('/items/<item_uuid>/ai/sequence')
@jwt_required
def prediction_for_sensor_item(item_uuid):
    filters = get_filters_from_request()
    start_date = request.args.get('startdate')
    end_date = request.args.get('enddate')
    sequence_data = get_sequence_for_sensor(item_uuid, filters, start_date, end_date)
    return response(200, sequence_data)

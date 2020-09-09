from distutils.util import strtobool
from typing import List, Any
from uuid import UUID

import flask
from flask import request
from flask_accept import accept, accept_fallback
from flask_jwt_extended import jwt_required, jwt_optional
from flask_restx import Resource, fields
from geoalchemy2.shape import to_shape
from shapely.geometry import Point
from shapely.geometry import mapping
from shapely_geojson import dumps, FeatureCollection

from app import api
from app.dto import ItemDTO
from app.handlers.flask import get_user_from_request
from app.models import Feature
from app.services.ai import generate_paths_from_points, get_sequence_for_sensor
from app.services.item import (
    get_collection_items,
    create_collection_item,
    add_collection_items,
    replace_collection_items,
    delete_collection_items,
    get_collection_item,
    delete_collection_item,
    get_collection_items_by_name,
    get_items,
    update_items,
    get_item,
    delete_item,
    update_item,
    update_collection_item,
)
from lib.visualizer.renderer import render_feature_collection, render_feature


class GeometryFormatter(fields.Raw):
    def format(self, value):
        return mapping(to_shape(value))


item_model = api.model(
    "Item",
    {
        "uuid": fields.String(description="uuid"),
        "collection_uuid": fields.String(description="collection_uuid"),
        "geometry": GeometryFormatter(),
        "properties": fields.Raw(description="properties"),
        "revision": fields.String(description="revision"),
        "created_at": fields.String(description="created_at"),
        "updated_at": fields.String(description="updated_at"),
    },
)

create_item_model = api.model(
    "CreateItem",
    {
        "geometry": GeometryFormatter(),
        "properties": fields.Wildcard(fields.String, description="properties"),
    },
)

update_item_model = api.model(
    "UpdateItem",
    {
        "geometry": GeometryFormatter(),
        "properties": fields.Wildcard(fields.String, description="properties"),
    },
)

bulk_create_item_response_model = api.model(
    "BulkItemResponse", {"uuid": fields.String(description="uuid")}
)


def valid_point(params):
    return "spatial_filter.point.x" in params and "spatial_filter.point.y" in params


def valid_envelope(params):
    if (
        "spatial_filter.envelope.ymin" in params
        and "spatial_filter.envelope.xmin" in params
        and "spatial_filter.envelope.ymax" in params
        and "spatial_filter.envelope.xmax" in params
    ):
        return True
    return False


def valid_distance(params):
    if (
        "spatial_filter.distance.x" in params
        and "spatial_filter.distance.y" in params
        and "spatial_filter.distance.d" in params
    ):
        return True
    return False


def get_spatial_filter(params):
    if not params.get("spatial_filter"):
        return None
    else:
        if params.get("spatial_filter") == "within-distance":
            if not valid_distance(params):
                return None
            else:
                return {
                    "filter": params.get("spatial_filter"),
                    "distance": {
                        "point": Point(
                            float(params.get("spatial_filter.distance.x")),
                            float(params.get("spatial_filter.distance.y")),
                        ),
                        "d": float(params.get("spatial_filter.distance.d")),
                    },
                }
        elif params.get("spatial_filter") in ["within", "intersect"] and valid_envelope(
            params
        ):
            return {
                "filter": params.get("spatial_filter"),
                "envelope": {
                    "ymin": float(params.get("spatial_filter.envelope.ymin")),
                    "xmin": float(params.get("spatial_filter.envelope.xmin")),
                    "ymax": float(params.get("spatial_filter.envelope.ymax")),
                    "xmax": float(params.get("spatial_filter.envelope.xmax")),
                },
            }
        elif params.get("spatial_filter") in ["within", "intersect"] and valid_point(
            params
        ):
            return {
                "filter": params.get("spatial_filter"),
                "point": {
                    "x": float(params.get("spatial_filter.point.x")),
                    "y": float(params.get("spatial_filter.point.y")),
                },
            }
        else:
            None


def get_collection_uuid_filter(params):
    value = params.get("collection_uuids")

    if not value:
        return None

    collection_uuids = value.split(",")
    return collection_uuids if len(collection_uuids) > 0 else None


def get_transforms_from_request():
    simplify = 0.0
    params = request.args

    if params is not None:
        simplify = float(params.get("simplify", simplify))

    return {"simplify": simplify}


def get_filters_from_request():
    offset = 0
    limit = 20
    property_filter = None
    valid = False
    spatial_filter = None
    collection_uuids = None
    params = request.args

    if params is not None:
        offset = int(params.get("offset", offset))
        limit = int(params.get("limit", limit))
        property_filter = params.get("property_filter", property_filter)
        valid = bool(strtobool(params.get("valid", "false")))
        spatial_filter = get_spatial_filter(params)
        collection_uuids = get_collection_uuid_filter(params)

    return {
        "offset": offset,
        "limit": limit,
        "property_filter": property_filter,
        "valid": valid,
        "spatial_filter": spatial_filter,
        "collection_uuids": collection_uuids,
    }


def get_visualizer_params_from_request():
    width = int(request.args.get("width", 1280))
    height = int(request.args.get("height", 1280))
    map_id = request.args.get("map_id", "dark-v10")

    return {"width": width, "height": height, "map_id": map_id}


def feature_collection_to_items(collection_uuid: UUID, geojson: Any) -> List[ItemDTO]:
    from shapely.geometry import shape

    items = [
        ItemDTO(
            **{
                "collection_uuid": collection_uuid,
                "geometry": shape(feature["geometry"]).to_wkt(),
                "properties": feature["properties"],
            }
        )
        for feature in geojson["features"]
    ]
    return items


ns = api.namespace("items", description="Item operations", path="/")

visualizer_params = {
    "width": {"description": "Resulting image width", "type": "int", "default": 1280},
    "height": {"description": "Resulting image height", "type": "int", "default": 1280},
    "map_id": {
        "description": "Mapbox style, valid ids = "
        + "[streets-v11, outdoors-v11, light-v10, dark-v10, satellite-v9, satellite-streets-v11]",
        "type": "string",
        "default": "dark-v10",
    },
}

get_params = {
    "offset": {"description": "offset", "type": "int", "default": 0},
    "limit": {"description": "limit", "type": "int", "default": 20},
    "valid": {"description": "valid", "type": "bool", "default": False},
}

filter_params = {
    "property_filter": {
        "description": "Property filter like someprop=X,otherprop=Y",
        "type": "string",
        "default": None,
    },
    "spatial_filter": {
        "description": "Spatial filter, one of within-distance, within, intersect",
        "type": "string",
        "default": None,
    },
    "spatial_filter.distance.x": {
        "description": "x (longitude) value of Point for within-distance",
        "type": "float",
    },
    "spatial_filter.distance.y": {
        "description": "y (latitude) value of Point for within-distance",
        "type": "float",
    },
    "spatial_filter.distance.d": {
        "description": "distance value from Point for within-distance",
        "type": "float",
    },
    "spatial_filter.envelope.ymin": {
        "description": "ymin of envelope for spatial filter within or intersect"
    },
    "spatial_filter.envelope.xmin": {
        "description": "xmin of envelope for spatial filter within or intersect"
    },
    "spatial_filter.envelope.ymax": {
        "description": "ymax of envelope for spatial filter within or intersect"
    },
    "spatial_filter.envelope.xmax": {
        "description": "xmax of envelope for spatial filter within or intersect"
    },
    "spatial_filter.point.x": {
        "description": "x (longitude) of point for spatial filter within or intersect"
    },
    "spatial_filter.point.y": {
        "description": "y (latitude) of point for spatial filter within or intersect"
    },
    "collection_uuids": {"description": "Comma-separated collection uuid filter"},
}

transform_params = {
    "simplify": {
        "description": "Tolerance for simplification of geometries",
        "type": "float",
        "default": 0.0,
    }
}

generate_walking_paths_params = {
    "steps": {
        "description": "Steps the agents will try to move in the environment",
        "type": "int",
        "default": 200,
    },
    "agents": {
        "description": "Number of agents to spawn in the simulation.",
        "type": "int",
        "default": 50,
    },
    "starting_points_collection_uuid": {
        "description": "Collection uuid to be used for starting points.",
        "type": "string",
        "default": None,
    },
    "environment_collection_uuid": {
        "description": "Collection to be used for environment.",
        "type": "string",
        "default": None,
    },
}

prediction_for_sensor_item_params = {
    "startdate": {
        "description": "A date presented in YY-mm-dd format",
        "type": "string",
        "default": None,
    },
    "enddate": {
        "description": "A date presented in YY-mm-dd format",
        "type": "string",
        "default": None,
    },
}


@ns.route("/items")
class ItemListApi(Resource):
    @accept_fallback
    @jwt_optional
    @ns.doc(
        "get_items",
        security=None,
        params={**get_params, **filter_params, **transform_params},
    )
    @ns.marshal_list_with(item_model)
    def get(self):
        user = get_user_from_request()
        filters = get_filters_from_request()
        transforms = get_transforms_from_request()
        items = get_items(user, filters, transforms)
        return items

    @get.support("application/geojson")
    @jwt_optional
    @ns.doc(
        "get_items",
        security=None,
        params={**get_params, **filter_params, **transform_params},
    )
    def get_geojson(self):
        user = get_user_from_request()
        filters = get_filters_from_request()
        transforms = get_transforms_from_request()
        items = get_items(user, filters, transforms)
        features = [
            Feature(to_shape(item.geometry), item.properties, str(item.uuid))
            for item in items
            if item.geometry is not None
        ]
        feature_collection = dumps(FeatureCollection(features))
        return flask.make_response(feature_collection, 200)

    @get.support("image/png")
    @jwt_optional
    @ns.doc(
        "get_items",
        security=None,
        params={**get_params, **filter_params, **transform_params, **visualizer_params},
    )
    def get_png(self):
        user = get_user_from_request()
        filters = get_filters_from_request()
        transforms = get_transforms_from_request()
        items = get_items(user, filters, transforms)
        features = [
            Feature(to_shape(item.geometry), item.properties, str(item.uuid))
            for item in items
            if item.geometry is not None
        ]
        feature_collection = FeatureCollection(features).__geo_interface__
        params = get_visualizer_params_from_request()
        data = render_feature_collection(
            feature_collection, params["width"], params["height"], params["map_id"]
        )
        return flask.make_response(data, 200, {"content-type": "image/png"})

    @accept("application/geojson")
    @jwt_required
    @ns.doc("update_items")
    @ns.marshal_list_with(bulk_create_item_response_model, code=201)
    def put(self):
        from shapely.geometry import shape

        user = get_user_from_request()
        geojson = request.get_json(force=True)
        items_new = [
            ItemDTO(
                **{
                    "uuid": feature["id"],
                    "geometry": shape(feature["geometry"]).to_wkt(),
                    "properties": feature["properties"],
                }
            )
            for feature in geojson["features"]
        ]

        items = update_items(user, items_new)

        return items, 201


@ns.route("/collections/<uuid:collection_uuid>/items")
class CollectionItemListApi(Resource):
    @accept_fallback
    @jwt_optional
    @ns.doc(
        "get_collection_items",
        security=None,
        params={**get_params, **filter_params, **transform_params},
    )
    @ns.marshal_list_with(item_model)
    def get(self, collection_uuid):
        user = get_user_from_request()
        filters = get_filters_from_request()
        transforms = get_transforms_from_request()
        items = get_collection_items(user, collection_uuid, filters, transforms)
        return items

    @get.support("application/geojson")
    @jwt_optional
    @ns.doc(
        "get_collection_items",
        security=None,
        params={**get_params, **filter_params, **transform_params},
    )
    def get_geojson(self, collection_uuid):
        user = get_user_from_request()
        filters = get_filters_from_request()
        transforms = get_transforms_from_request()
        items = get_collection_items(user, collection_uuid, filters, transforms)
        features = [
            Feature(to_shape(item.geometry), item.properties, str(item.uuid))
            for item in items
            if item.geometry is not None
        ]
        feature_collection = dumps(FeatureCollection(features))
        return flask.make_response(feature_collection, 200)

    @get.support("image/png")
    @jwt_optional
    @ns.doc(
        "get_collection_items",
        security=None,
        params={**get_params, **filter_params, **transform_params, **visualizer_params},
    )
    def get_png(self, collection_uuid):
        user = get_user_from_request()
        filters = get_filters_from_request()
        transforms = get_transforms_from_request()
        items = get_collection_items(user, collection_uuid, filters, transforms)
        features = [
            Feature(to_shape(item.geometry), item.properties, str(item.uuid))
            for item in items
            if item.geometry is not None
        ]
        feature_collection = FeatureCollection(features).__geo_interface__
        params = get_visualizer_params_from_request()
        data = render_feature_collection(
            feature_collection, params["width"], params["height"], params["map_id"]
        )
        return flask.make_response(data, 200, {"content-type": "image/png"})

    @accept("application/json")
    @jwt_required
    @ns.doc("create_collection_item")
    @ns.expect(create_item_model)
    @ns.marshal_with(item_model, code=201)
    def post(self, collection_uuid):
        user = get_user_from_request()
        item_new = ItemDTO(**request.get_json())
        item = create_collection_item(user, collection_uuid, item_new)
        return item, 201

    @post.support("application/geojson")
    @jwt_required
    @ns.doc("replace_collection_items")
    @ns.expect(create_item_model)
    @ns.marshal_list_with(bulk_create_item_response_model, code=201)
    def post_geojson(self, collection_uuid):
        user = get_user_from_request()
        geojson = request.get_json(force=True)
        items = feature_collection_to_items(collection_uuid, geojson)

        items = replace_collection_items(user, collection_uuid, items)

        return items, 201

    @accept("application/geojson")
    @jwt_required
    @ns.doc("add_collection_items")
    @ns.marshal_list_with(bulk_create_item_response_model, code=201)
    def put(self, collection_uuid):
        user = get_user_from_request()
        geojson = request.get_json(force=True)
        items = feature_collection_to_items(collection_uuid, geojson)

        items = add_collection_items(user, collection_uuid, items)

        return items, 201

    @accept_fallback
    @jwt_required
    @ns.doc("delete_collection_items")
    def delete(self, collection_uuid):
        user = get_user_from_request()
        delete_collection_items(user, collection_uuid)
        return "", 204


@ns.route("/collections/<uuid:collection_uuid>/items/<uuid:item_uuid>")
@ns.response(404, "Item not found")
@ns.param("collection_uuid", "The collection identifier")
@ns.param("item_uuid", "The item identifier")
class CollectionItemApi(Resource):
    @accept_fallback
    @jwt_optional
    @ns.doc("get_item", security=None)
    @ns.marshal_with(item_model)
    def get(self, collection_uuid, item_uuid):
        user = get_user_from_request()
        item = get_collection_item(user, collection_uuid, item_uuid)
        return item

    @get.support("application/geojson")
    @jwt_optional
    @ns.doc("get_item", security=None)
    def get_geojson(self, collection_uuid, item_uuid):
        user = get_user_from_request()
        item = get_collection_item(user, collection_uuid, item_uuid)
        feature = Feature(to_shape(item.geometry), item.properties, str(item.uuid))
        return flask.make_response(dumps(feature), 200)

    @get.support("image/png")
    @jwt_optional
    @ns.doc(
        "get_item",
        security=None,
        params={**get_params, **filter_params, **transform_params, **visualizer_params},
    )
    def get_png(self, collection_uuid, item_uuid):
        user = get_user_from_request()
        item = get_collection_item(user, collection_uuid, item_uuid)
        feature = Feature(to_shape(item.geometry), item.properties).__geo_interface__
        params = get_visualizer_params_from_request()
        data = render_feature(
            feature, params["width"], params["height"], params["map_id"]
        )
        return flask.make_response(data, 200, {"content-type": "image/png"})

    @accept_fallback
    @jwt_required
    @ns.doc("delete_item")
    def delete(self, collection_uuid, item_uuid):
        user = get_user_from_request()
        delete_collection_item(user, collection_uuid, item_uuid)
        return "", 204

    @accept_fallback
    @jwt_required
    @ns.doc("update_item")
    @ns.expect(update_item_model)
    def put(self, collection_uuid, item_uuid):
        user = get_user_from_request()
        item_update = ItemDTO(**request.get_json(force=True))
        update_collection_item(user, collection_uuid, item_uuid, item_update)
        return "", 204


@ns.route("/collections/by_name/<collection_name>/items")
@ns.param("collection_name", "The collection name")
class CollectionByNameItemListApi(Resource):
    @accept_fallback
    @jwt_optional
    @ns.doc(
        "get_collection_items_by_name",
        security=None,
        params={**get_params, **filter_params, **transform_params},
    )
    @ns.marshal_list_with(item_model)
    def get(self, collection_name):
        user = get_user_from_request()
        filters = get_filters_from_request()
        transforms = get_transforms_from_request()
        items = get_collection_items_by_name(user, collection_name, filters, transforms)
        return items

    @jwt_optional
    @get.support("application/geojson")
    @ns.doc(
        "get_collection_items_by_name",
        security=None,
        params={**get_params, **filter_params, **transform_params},
    )
    def get_geojson(self, collection_name):
        user = get_user_from_request()
        filters = get_filters_from_request()
        transforms = get_transforms_from_request()
        items = get_collection_items_by_name(user, collection_name, filters, transforms)
        features = [
            Feature(to_shape(item.geometry), item.properties, str(item.uuid))
            for item in items
            if item.geometry is not None
        ]
        feature_collection = dumps(FeatureCollection(features))
        return flask.make_response(feature_collection, 200)

    @get.support("image/png")
    @jwt_optional
    @ns.doc(
        "get_collection_items_by_name",
        security=None,
        params={**get_params, **filter_params, **transform_params, **visualizer_params},
    )
    def get_png(self, collection_name):
        filters = get_filters_from_request()
        user = get_user_from_request()
        transforms = get_transforms_from_request()
        items = get_collection_items_by_name(user, collection_name, filters, transforms)
        features = [
            Feature(to_shape(item.geometry), item.properties)
            for item in items
            if item.geometry is not None
        ]
        feature_collection = FeatureCollection(features).__geo_interface__
        params = get_visualizer_params_from_request()
        data = render_feature_collection(
            feature_collection, params["width"], params["height"], params["map_id"]
        )
        return flask.make_response(data, 200, {"content-type": "image/png"})


@ns.route("/items/<uuid:item_uuid>")
@ns.response(404, "Item not found")
@ns.param("item_uuid", "The item identifier")
class ItemApi(Resource):
    @accept_fallback
    @jwt_optional
    @ns.doc(
        "get_item",
        security=None,
        params={**get_params, **filter_params, **transform_params},
    )
    @ns.marshal_with(item_model)
    def get(self, item_uuid):
        user = get_user_from_request()
        item = get_item(user, item_uuid)
        return item

    @get.support("application/geojson")
    @jwt_optional
    @ns.doc(
        "get_item",
        security=None,
        params={**get_params, **filter_params, **transform_params},
    )
    def get_geojson(self, item_uuid):
        user = get_user_from_request()
        item = get_item(user, item_uuid)
        feature = Feature(to_shape(item.geometry), item.properties)
        return flask.make_response(dumps(feature), 200)

    @get.support("image/png")
    @jwt_optional
    @ns.doc(
        "get_item",
        security=None,
        params={**get_params, **filter_params, **transform_params, **visualizer_params},
    )
    def get_png(self, item_uuid):
        user = get_user_from_request()
        item = get_item(user, item_uuid)
        feature = Feature(to_shape(item.geometry), item.properties).__geo_interface__
        params = get_visualizer_params_from_request()
        data = render_feature(
            feature, params["width"], params["height"], params["map_id"]
        )
        return flask.make_response(data, 200, {"content-type": "image/png"})

    @accept_fallback
    @jwt_required
    @ns.doc("delete_item")
    def delete(self, item_uuid):
        user = get_user_from_request()
        delete_item(user, item_uuid)
        return "", 204

    @accept_fallback
    @jwt_required
    @ns.doc("update_item")
    @ns.expect(update_item_model)
    def put(self, item_uuid):
        user = get_user_from_request()
        item_update = ItemDTO(**request.get_json(force=True))
        update_item(user, item_uuid, item_update)
        return "", 204


@ns.route("/collections/<collection_uuid>/items/ai/generate/walkingpaths")
@ns.param("collection_uuid", "The collection identifier")
class GenerateWalkingPathsApi(Resource):
    @jwt_required
    @ns.marshal_list_with(bulk_create_item_response_model)
    @ns.doc(
        "generate_walking_paths",
        security=None,
        params={**generate_walking_paths_params},
    )
    def post(self, collection_uuid):
        user = get_user_from_request()
        filters = get_filters_from_request()
        filters.update(
            {"offset": 0, "limit": 1000, "property_filter": None, "valid": False}
        )
        steps = min(int(request.args.get("steps", "200")), 200)
        n_agents = min(int(request.args.get("agents", "50")), 50)
        starting_points_collection_uuid = request.args.get(
            "starting_points_collection_uuid"
        )
        environment_collection_uuid = request.args.get("environment_collection_uuid")
        items = generate_paths_from_points(
            starting_points_collection_uuid,
            environment_collection_uuid,
            collection_uuid,
            n_agents,
            steps,
            user,
            filters,
        )
        return items, 201


@ns.route("/items/<item_uuid>/ai/sequence")
@ns.param("item_uuid", "The item identifier")
class PredictionForSensorItemApi(Resource):
    @jwt_optional
    @ns.doc(
        "prediction_for_sensor_item",
        security=None,
        params={**prediction_for_sensor_item_params},
    )
    def get(self, item_uuid):
        user = get_user_from_request()
        start_date = request.args.get("startdate")
        end_date = request.args.get("enddate")
        sequence_data = get_sequence_for_sensor(user, item_uuid, start_date, end_date)
        return sequence_data, 200

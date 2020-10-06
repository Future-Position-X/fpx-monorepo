from enum import Enum
from typing import Any, List, Optional, Union
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query
from geoalchemy2.shape import to_shape
from geojson_pydantic.features import Feature, FeatureCollection
from shapely.geometry import Point, shape
from starlette.responses import Response, StreamingResponse
from starlette.status import HTTP_204_NO_CONTENT

from app import models, schemas, services
from app.api import deps
from app.dto import ItemDTO
from lib.visualizer.renderer import render_feature, render_feature_collection

router = APIRouter()


def collection_uuid_filter(
    collection_uuids: Optional[str] = Query(None),
) -> Optional[List[str]]:
    if not collection_uuids:
        return None

    collection_uuids_arr = collection_uuids.split(",")
    return collection_uuids_arr if len(collection_uuids_arr) > 0 else None


def transforms_parameters(simplify: Optional[float] = Query(0.0)) -> dict:
    return {"simplify": simplify}


def spatial_filter_parameters(
    spatial_filter: Optional[str] = Query(None),
    spatial_filter_distance_x: Optional[float] = Query(
        None, alias="spatial_filter.distance.x"
    ),
    spatial_filter_distance_y: Optional[float] = Query(
        None, alias="spatial_filter.distance.y"
    ),
    spatial_filter_distance_d: Optional[float] = Query(
        None, alias="spatial_filter.distance.d"
    ),
    spatial_filter_envelope_ymin: Optional[float] = Query(
        None, alias="spatial_filter.envelope.ymin"
    ),
    spatial_filter_envelope_xmin: Optional[float] = Query(
        None, alias="spatial_filter.envelope.xmin"
    ),
    spatial_filter_envelope_ymax: Optional[float] = Query(
        None, alias="spatial_filter.envelope.ymax"
    ),
    spatial_filter_envelope_xmax: Optional[float] = Query(
        None, alias="spatial_filter.envelope.xmax"
    ),
    spatial_filter_point_x: Optional[float] = Query(
        None, alias="spatial_filter.point.x"
    ),
    spatial_filter_point_y: Optional[float] = Query(
        None, alias="spatial_filter.point.y"
    ),
) -> Optional[dict]:
    if not spatial_filter:
        return None
    else:
        if spatial_filter == "within-distance":
            if not (
                spatial_filter_distance_x
                and spatial_filter_distance_y
                and spatial_filter_distance_d
            ):
                raise ValueError
            else:
                return {
                    "filter": spatial_filter,
                    "distance": {
                        "point": Point(
                            spatial_filter_distance_x, spatial_filter_distance_y
                        ),
                        "d": spatial_filter_distance_d,
                    },
                }
        elif spatial_filter in ["within", "intersect"] and (
            spatial_filter_envelope_ymin
            and spatial_filter_envelope_xmin
            and spatial_filter_envelope_ymax
            and spatial_filter_envelope_xmax
        ):
            return {
                "filter": spatial_filter,
                "envelope": {
                    "ymin": spatial_filter_envelope_ymin,
                    "xmin": spatial_filter_envelope_xmin,
                    "ymax": spatial_filter_envelope_ymax,
                    "xmax": spatial_filter_envelope_xmax,
                },
            }
        elif spatial_filter in ["within", "intersect"] and (
            spatial_filter_point_x and spatial_filter_point_y
        ):
            return {
                "filter": spatial_filter,
                "point": {"x": spatial_filter_point_x, "y": spatial_filter_point_y},
            }
        else:
            raise ValueError


def visualizer_parameters(
    width: Optional[int] = Query(1280),
    height: Optional[int] = Query(1280),
    map_id: Optional[str] = Query("dark-v10"),
) -> dict:
    return {"width": width, "height": height, "map_id": map_id}


def filter_parameters(
    offset: Optional[int] = Query(0),
    limit: Optional[int] = Query(20),
    property_filter: Optional[str] = Query(None),
    valid: Optional[bool] = Query(False),
    spatial_filter: Optional[dict] = Depends(spatial_filter_parameters),
    collection_uuids: Optional[list] = Depends(collection_uuid_filter),
) -> dict:
    return {
        "offset": offset,
        "limit": limit,
        "property_filter": property_filter,
        "valid": valid,
        "spatial_filter": spatial_filter,
        "collection_uuids": collection_uuids,
    }


# TODO: Figure out where to put this method
def map_item_dto_to_feature(item: ItemDTO) -> Optional[Feature]:
    feature = None
    if item.geometry is not None:
        feature = Feature(
            geometry=to_shape(item.geometry),
            properties=item.properties,
            id=str(item.uuid),
        )
    return feature


# TODO: Figure out where to put this method
def map_item_dtos_to_features(items: List[ItemDTO]) -> List[Feature]:
    features = list(filter(None, [map_item_dto_to_feature(item) for item in items]))
    return features


# TODO: Figure out where to put this method
def map_feature_to_item_dto(feature: Feature) -> ItemDTO:
    item = ItemDTO(
        **{
            "uuid": feature.id,
            "geometry": shape(feature.geometry).to_wkt(),
            "properties": feature.properties,
        }
    )
    return item


# TODO: Figure out where to put this method
def map_features_to_item_dtos(features: List[Feature]) -> List[ItemDTO]:
    items = [map_feature_to_item_dto(feature) for feature in features]
    return items


class ItemRequestAcceptHeaders(Enum):
    json = "application/json"
    geojson = "application/geojson"
    png = "image/png"
    any = "*/*"


@router.get(
    "/items",
    response_model=Union[List[schemas.Item], FeatureCollection],
    responses={
        200: {
            "description": "Items requested",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/Item"},
                    }
                },
                "application/geojson": {
                    "schema": {"$ref": "#/components/schemas/FeatureCollection"}
                },
                "image/png": {"schema": {"type": "string", "format": "binary"}},
            },
        }
    },
)
def get_items(
    filter_params: dict = Depends(filter_parameters),
    transforms_params: dict = Depends(transforms_parameters),
    visualizer_params: dict = Depends(visualizer_parameters),
    current_user: models.User = Depends(deps.get_current_user_or_guest),
    accept: ItemRequestAcceptHeaders = Header(ItemRequestAcceptHeaders.json),
) -> Union[List[schemas.Item], FeatureCollection, StreamingResponse]:
    """
    Retrieve items.
    """

    items = services.item.get_items(current_user, filter_params, transforms_params)
    if accept in [ItemRequestAcceptHeaders.geojson, ItemRequestAcceptHeaders.png]:
        features = map_item_dtos_to_features(items)
        feature_collection = FeatureCollection(features=features)
        if accept == ItemRequestAcceptHeaders.geojson:
            return feature_collection
        elif accept == ItemRequestAcceptHeaders.png:
            data = render_feature_collection(
                feature_collection.dict(),
                visualizer_params["width"],
                visualizer_params["height"],
                visualizer_params["map_id"],
            )
            return StreamingResponse(data, media_type="image/png")

    return [schemas.Item.from_dto(item) for item in items]


@router.put(
    "/items",
    status_code=204,
    responses={
        204: {
            "description": "Update items",
            "content": {"application/json": {}, "application/geojson": {}},
        }
    },
)
def update_items(
    items_in: Union[List[schemas.ItemUpdate], FeatureCollection],
    current_user: models.User = Depends(deps.get_current_user),
    accept: str = Header(None),
    content_type: str = Header(None),
) -> Response:
    items_updates = None
    # TODO: Should check content_type
    if isinstance(items_in, FeatureCollection):
        items_updates = map_features_to_item_dtos(items_in.features)
    else:
        items_updates = [item.to_dto() for item in items_in]

    services.item.update_items(current_user, items_updates)
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.get(
    "/collections/{collection_uuid}/items",
    response_model=Union[List[schemas.Item], FeatureCollection],
    responses={
        200: {
            "description": "Collection items requested",
            "content": {
                "application/json": {},
                "application/geojson": {
                    "schema": {"$ref": "#/components/schemas/FeatureCollection"}
                },
                "image/png": {},
            },
        }
    },
)
def get_collection_items(
    collection_uuid: UUID,
    filter_params: dict = Depends(filter_parameters),
    transforms_params: dict = Depends(transforms_parameters),
    visualizer_params: dict = Depends(visualizer_parameters),
    current_user: models.User = Depends(deps.get_current_user_or_guest),
    accept: str = Header(None),
) -> Any:
    """
    Retrieve items.
    """

    items = services.item.get_collection_items(
        current_user, collection_uuid, filter_params, transforms_params
    )

    if accept in [None, "*/*", "application/json"]:
        return [schemas.Item.from_dto(item) for item in items]
    else:
        features = map_item_dtos_to_features(items)
        feature_collection = FeatureCollection(features=features)
        if accept == "application/geojson":
            return feature_collection
        elif accept == "image/png":
            data = render_feature_collection(
                feature_collection.dict(),
                visualizer_params["width"],
                visualizer_params["height"],
                visualizer_params["map_id"],
            )
            return StreamingResponse(data, media_type="image/png")


@router.post(
    "/collections/{collection_uuid}/items",
    response_model=Union[schemas.Item, Feature],
    status_code=201,
    responses={201: {"description": "Create collection item"}},
)
def create_collection_item(
    collection_uuid: UUID,
    item_in: Union[schemas.ItemCreate, Feature],
    current_user: models.User = Depends(deps.get_current_user),
    accept: str = Header(None),
    content_type: str = Header(None),
) -> Union[Optional[Feature], schemas.Item]:
    item_create = None
    # TODO: Should check content_type
    if isinstance(item_in, Feature):
        item_create = map_feature_to_item_dto(item_in)
    else:
        item_create = item_in.to_dto()

    item = services.item.create_collection_item(
        current_user, collection_uuid, item_create
    )
    if accept == "application/geojson":
        feature = map_item_dto_to_feature(item)
        return feature
    else:
        return schemas.Item.from_dto(item)


@router.put(
    "/collections/{collection_uuid}/items",
    status_code=204,
    responses={
        201: {
            "description": "Update items",
            "content": {"application/json": {}, "application/geojson": {}},
        }
    },
)
def update_collection_items(
    collection_uuid: UUID,
    items_in: Union[List[schemas.ItemUpdate], FeatureCollection],
    current_user: models.User = Depends(deps.get_current_user),
    accept: str = Header(None),
    content_type: str = Header(None),
) -> Response:
    items_updates = None
    # TODO: Should check content_type
    if isinstance(items_in, FeatureCollection):
        items_updates = map_features_to_item_dtos(items_in.features)
    else:
        items_updates = [item.to_dto() for item in items_in]

    services.item.update_collection_items(current_user, collection_uuid, items_updates)
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.post(
    "/collections/{collection_uuid}/items/replace",
    response_model=Union[List[schemas.Item], FeatureCollection],
    status_code=201,
    responses={
        201: {
            "description": "Replace all items in collection",
            "content": {
                "application/json": {},
                "application/geojson": {
                    "schema": {"$ref": "#/components/schemas/FeatureCollection"}
                },
            },
        }
    },
)
def replace_collection_items(
    collection_uuid: UUID,
    items_in: Union[List[schemas.ItemUpdate], FeatureCollection],
    current_user: models.User = Depends(deps.get_current_user),
    accept: str = Header(None),
    content_type: str = Header(None),
) -> Union[FeatureCollection, List[schemas.Item]]:
    items = None
    # TODO: Should check content_type
    if isinstance(items_in, FeatureCollection):
        items = map_features_to_item_dtos(items_in.features)
    else:
        items = [item.to_dto() for item in items_in]

    items = services.item.replace_collection_items(current_user, collection_uuid, items)

    if accept == "application/geojson":
        features = map_item_dtos_to_features(items)
        feature_collection = FeatureCollection(features=features)
        return feature_collection
    else:
        return [schemas.Item.from_dto(item) for item in items]


@router.post(
    "/collections/{collection_uuid}/items/bulk",
    response_model=Union[List[schemas.Item], FeatureCollection],
    status_code=201,
    responses={
        201: {
            "description": "Create items in collection",
            "content": {
                "application/json": {},
                "application/geojson": {
                    "schema": {"$ref": "#/components/schemas/FeatureCollection"}
                },
            },
        }
    },
)
def create_collection_items(
    collection_uuid: UUID,
    items_in: Union[List[schemas.ItemUpdate], FeatureCollection],
    current_user: models.User = Depends(deps.get_current_user),
    accept: str = Header(None),
    content_type: str = Header(None),
) -> Union[FeatureCollection, List[schemas.Item]]:
    items = None
    # TODO: Should check content_type
    if isinstance(items_in, FeatureCollection):
        items = map_features_to_item_dtos(items_in.features)
    else:
        items = [item.to_dto() for item in items_in]

    items = services.item.add_collection_items(current_user, collection_uuid, items)

    if accept == "application/geojson":
        features = map_item_dtos_to_features(items)
        feature_collection = FeatureCollection(features=features)
        return feature_collection
    else:
        return [schemas.Item.from_dto(item) for item in items]


@router.delete(
    "/collections/{collection_uuid}/items",
    status_code=204,
    responses={
        204: {
            "description": "Delete items in collection",
            "content": {"application/json": {}, "application/geojson": {}},
        }
    },
)
def delete_collection_items(
    collection_uuid: UUID, current_user: models.User = Depends(deps.get_current_user)
) -> Response:
    services.item.delete_collection_items(current_user, collection_uuid)
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.get(
    "/collections/{collection_uuid}/items/{item_uuid}",
    response_model=Union[schemas.Item, Feature],
    status_code=200,
    responses={
        200: {
            "description": "Get item in collection",
            "content": {
                "application/json": {},
                "application/geojson": {
                    "schema": {"$ref": "#/components/schemas/Feature"}
                },
                "image/png": {},
            },
        }
    },
)
def get_collection_item(
    collection_uuid: UUID,
    item_uuid: UUID,
    visualizer_params: dict = Depends(visualizer_parameters),
    current_user: models.User = Depends(deps.get_current_user_or_guest),
    accept: str = Header(None),
) -> Union[schemas.Item, Feature, StreamingResponse]:
    item = services.item.get_collection_item(current_user, collection_uuid, item_uuid)

    if accept in ["application/geojson", "image/png"]:
        feature = map_item_dto_to_feature(item)
        assert feature is not None
        if accept == "image/png":
            data = render_feature(
                feature.dict(),
                visualizer_params["width"],
                visualizer_params["height"],
                visualizer_params["map_id"],
            )
            return StreamingResponse(data, media_type="image/png")
        else:  # "application/geojson"
            return feature
    else:
        return schemas.Item.from_dto(item)


@router.delete(
    "/collections/{collection_uuid}/items/{item_uuid}",
    status_code=204,
    responses={
        204: {
            "description": "Delete item in collection",
            "content": {"application/json": {}, "application/geojson": {}},
        }
    },
)
def delete_collection_item(
    collection_uuid: UUID,
    item_uuid: UUID,
    current_user: models.User = Depends(deps.get_current_user),
) -> Response:
    services.item.delete_collection_item(current_user, collection_uuid, item_uuid)
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.put(
    "/collections/{collection_uuid}/items/{item_uuid}",
    status_code=204,
    responses={
        204: {
            "description": "Update collection item",
            "content": {"application/json": {}, "application/geojson": {}},
        }
    },
)
def update_collection_item(
    collection_uuid: UUID,
    item_uuid: UUID,
    item_in: Union[schemas.ItemUpdate, Feature],
    current_user: models.User = Depends(deps.get_current_user),
    accept: str = Header(None),
    content_type: str = Header(None),
) -> Response:
    item_update = None
    # TODO: Should check content_type
    if isinstance(item_in, Feature):
        item_update = map_feature_to_item_dto(item_in)
    else:
        item_update = item_in.to_dto()

    services.item.update_collection_item(
        current_user, collection_uuid, item_uuid, item_update
    )
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.get(
    "/collections/by_name/{collection_name}/items",
    response_model=Union[List[schemas.Item], FeatureCollection],
    responses={
        200: {
            "description": "Collection items by collection name",
            "content": {
                "application/json": {},
                "application/geojson": {
                    "schema": {"$ref": "#/components/schemas/FeatureCollection"}
                },
                "image/png": {},
            },
        }
    },
)
def get_collection_items_by_name(
    collection_name: str,
    filter_params: dict = Depends(filter_parameters),
    transforms_params: dict = Depends(transforms_parameters),
    visualizer_params: dict = Depends(visualizer_parameters),
    current_user: models.User = Depends(deps.get_current_user_or_guest),
    accept: str = Header(None),
) -> Any:
    """
    Retrieve items.
    """

    items = services.item.get_collection_items_by_name(
        current_user, collection_name, filter_params, transforms_params
    )
    if accept is None or accept == "application/json":
        return [schemas.Item.from_dto(item) for item in items]
    else:
        features = map_item_dtos_to_features(items)
        feature_collection = FeatureCollection(features=features)
        if accept == "application/geojson":
            return feature_collection
        elif accept == "image/png":
            data = render_feature_collection(
                feature_collection.dict(),
                visualizer_params["width"],
                visualizer_params["height"],
                visualizer_params["map_id"],
            )
            return StreamingResponse(data, media_type="image/png")


@router.get(
    "/items/{item_uuid}",
    response_model=Union[schemas.Item, Feature],
    status_code=200,
    responses={
        200: {
            "description": "Get item",
            "content": {
                "application/json": {},
                "application/geojson": {
                    "schema": {"$ref": "#/components/schemas/Feature"}
                },
                "image/png": {},
            },
        }
    },
)
def get_item(
    item_uuid: UUID,
    visualizer_params: dict = Depends(visualizer_parameters),
    current_user: models.User = Depends(deps.get_current_user_or_guest),
    accept: str = Header(None),
) -> Union[Feature, schemas.Item, StreamingResponse]:
    item = services.item.get_item(current_user, item_uuid)

    if accept in ["application/geojson", "image/png"]:
        feature = map_item_dto_to_feature(item)
        assert feature is not None
        if accept == "image/png":
            data = render_feature(
                feature.dict(),
                visualizer_params["width"],
                visualizer_params["height"],
                visualizer_params["map_id"],
            )
            return StreamingResponse(data, media_type="image/png")
        else:  # "application/geojson":
            return feature
    else:
        return schemas.Item.from_dto(item)


@router.delete(
    "/items/{item_uuid}",
    status_code=204,
    responses={
        204: {
            "description": "Delete item",
            "content": {"application/json": {}, "application/geojson": {}},
        }
    },
)
def delete_item(
    item_uuid: UUID, current_user: models.User = Depends(deps.get_current_user)
) -> Response:
    services.item.delete_item(current_user, item_uuid)
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.put(
    "/items/{item_uuid}",
    status_code=204,
    responses={
        204: {
            "description": "Update item",
            "content": {"application/json": {}, "application/geojson": {}},
        }
    },
)
def update_item(
    item_uuid: UUID,
    item_in: Union[schemas.ItemUpdate, Feature],
    current_user: models.User = Depends(deps.get_current_user),
    accept: str = Header(None),
    content_type: str = Header(None),
) -> Response:
    item_update = None
    # TODO: Should check content_type
    if isinstance(item_in, Feature):
        item_update = map_feature_to_item_dto(item_in)
    else:
        item_update = item_in.to_dto()

    services.item.update_item(current_user, item_uuid, item_update)
    return Response(status_code=HTTP_204_NO_CONTENT)

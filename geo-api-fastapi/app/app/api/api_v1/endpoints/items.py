from enum import Enum
from typing import Any, List, Union, Optional
import logging
from uuid import UUID

from app.dto import ItemDTO
from fastapi import APIRouter, Depends, HTTPException, Header, Request, Query
from geoalchemy2.shape import to_shape, from_shape
from geojson_pydantic.geometries import Geometry
from lib.visualizer.renderer import render_feature_collection
from sqlalchemy.orm import Session

from app import crud, models, schemas, services
from app.api import deps

from shapely.geometry import Point, shape
from starlette.responses import StreamingResponse

router = APIRouter()
from geojson_pydantic.features import FeatureCollection, Feature


def collection_uuid_filter(collection_uuids: Optional[str] = Query(None)):
    if not collection_uuids:
        return None

    collection_uuids_arr = collection_uuids.split(",")
    return collection_uuids_arr if len(collection_uuids_arr) > 0 else None


def transforms_parameters(simplify: Optional[float] = Query(0.0)):
    return {"simplify": simplify}


def spatial_filter_parameters(spatial_filter: Optional[str] = Query(None),
                              spatial_filter_distance_x: Optional[float] = Query(None,
                                                                                 alias="spatial_filter.distance.x"),
                              spatial_filter_distance_y: Optional[float] = Query(None,
                                                                                 alias="spatial_filter.distance.y"),
                              spatial_filter_distance_d: Optional[float] = Query(None,
                                                                                 alias="spatial_filter.distance.d"),
                              spatial_filter_envelope_ymin: Optional[float] = Query(None,
                                                                                    alias="spatial_filter.envelope.ymin"),
                              spatial_filter_envelope_xmin: Optional[float] = Query(None,
                                                                                    alias="spatial_filter.envelope.xmin"),
                              spatial_filter_envelope_ymax: Optional[float] = Query(None,
                                                                                    alias="spatial_filter.envelope.ymax"),
                              spatial_filter_envelope_xmax: Optional[float] = Query(None,
                                                                                    alias="spatial_filter.envelope.xmax"),
                              spatial_filter_point_x: Optional[float] = Query(None, alias="spatial_filter.point.x"),
                              spatial_filter_point_y: Optional[float] = Query(None, alias="spatial_filter.point.y"),
                              ):
    if not spatial_filter:
        return None
    else:
        if spatial_filter == "within-distance":
            if not (spatial_filter_distance_x and spatial_filter_distance_y and spatial_filter_distance_d):
                raise ValueError
            else:
                return {
                    "filter": spatial_filter,
                    "distance": {
                        "point": Point(
                            spatial_filter.distance_x,
                            spatial_filter_distance_y,
                        ),
                        "d": spatial_filter_distance_d,
                    },
                }
        elif spatial_filter in ["within", "intersect"] and (
                spatial_filter_envelope_ymin and spatial_filter_envelope_xmin and spatial_filter_envelope_ymax and spatial_filter_envelope_xmax):
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
                "point": {
                    "x": spatial_filter_point_x,
                    "y": spatial_filter_point_y,
                },
            }
        else:
            raise ValueError


def visualizer_parameters(width: Optional[int] = Query(1280),
                          height: Optional[int] = Query(1280),
                          map_id: Optional[str] = Query("dark-v10")):
    return {"width": width, "height": height, "map_id": map_id}


def filter_parameters(offset: Optional[int] = Query(0),
                      limit: Optional[int] = Query(20),
                      property_filter: Optional[str] = Query(None),
                      valid: Optional[bool] = Query(False),
                      spatial_filter: Optional[dict] = Depends(spatial_filter_parameters),
                      collection_uuids: Optional[list] = Depends(collection_uuid_filter)
                      ):
    return {"offset": offset,
            "limit": limit,
            "property_filter": property_filter,
            "valid": valid,
            "spatial_filter": spatial_filter,
            "collection_uuids": collection_uuids,
            }


# TODO: Figure out where to put this method
def map_item_dto_to_feature(item: ItemDTO) -> Feature:
    feature = None
    if item.geometry is not None:
        feature = Feature(geometry=to_shape(item.geometry), properties=item.properties, id=str(item.uuid))
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


@router.get("/items", response_model=Union[List[schemas.Item], FeatureCollection], responses={
    200: {
        "description": "Items requested",
        "content": {
            "application/json": {
                "example": {"id": "bar", "value": "The bar tenders"}
            },
            "application/geojson": {
                "example": {"id": "bar", "value": "The bar tenders"},
                "schema": {
                    "$ref": "#/components/schemas/FeatureCollection"
                }
            },
            "image/png": {},
        }
    }
})
def get_items(
        filter_params: dict = Depends(filter_parameters),
        transforms_params: dict = Depends(transforms_parameters),
        visualizer_params: dict = Depends(visualizer_parameters),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user_or_guest),
        accept: str = Header(None),
) -> Any:
    """
    Retrieve items.
    """

    items = services.item.get_items(current_user, filter_params, transforms_params)
    if accept == None or accept == "application/json":
        return [schemas.Item.from_dto(item) for item in items]
    else:
        features = map_item_dtos_to_features(items)
        feature_collection = FeatureCollection(features=features)
        if accept == "application/geojson":
            return feature_collection
        elif accept == "image/png":
            data = render_feature_collection(
                feature_collection.dict(), visualizer_params["width"], visualizer_params["height"],
                visualizer_params["map_id"]
            )
            return StreamingResponse(data, media_type="image/png")


@router.put("/items", response_model=Union[List[schemas.Item], FeatureCollection], status_code=201, responses={
    201: {
        "description": "Update items",
        "content": {
            "application/json": {},
            "application/geojson": {
                "schema": {
                    "$ref": "#/components/schemas/FeatureCollection"
                }
            },
        }
    }
})
def update_items(
        items_in: Union[List[schemas.ItemUpdate], FeatureCollection],
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user_or_guest),
        accept: str = Header(None),
        content_type: str = Header(None),
):
    items_updates = None
    # TODO: Should check content_type
    if type(items_in) == FeatureCollection:
        items_updates = map_features_to_item_dtos(items_in.features)
    else:
        items_updates = [item.to_dto() for item in items_in]

    items = services.update_items(current_user, items_updates)

    if accept == "application/geojson":
        features = map_item_dtos_to_features(items)
        feature_collection = FeatureCollection(features=features)
        return feature_collection
    else:
        return [schemas.Item.from_dto(item) for item in items]


@router.get("/collections/{collection_uuid}/items", response_model=Union[List[schemas.Item], FeatureCollection], responses={
    200: {
        "description": "Collection items requested",
        "content": {
            "application/json": {
                "example": {"id": "bar", "value": "The bar tenders"}
            },
            "application/geojson": {
                "example": {"id": "bar", "value": "The bar tenders"},
                "schema": {
                    "$ref": "#/components/schemas/FeatureCollection"
                }
            },
            "image/png": {},
        }
    }
})
def get_collection_items(
        collection_uuid: UUID,
        filter_params: dict = Depends(filter_parameters),
        transforms_params: dict = Depends(transforms_parameters),
        visualizer_params: dict = Depends(visualizer_parameters),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user_or_guest),
        accept: str = Header(None),
) -> Any:
    """
    Retrieve items.
    """

    items = services.item.get_collection_items(current_user, collection_uuid, filter_params, transforms_params)
    if accept == None or accept == "application/json":
        return [schemas.Item.from_dto(item) for item in items]
    else:
        features = map_item_dtos_to_features(items)
        feature_collection = FeatureCollection(features=features)
        if accept == "application/geojson":
            return feature_collection
        elif accept == "image/png":
            data = render_feature_collection(
                feature_collection.dict(), visualizer_params["width"], visualizer_params["height"],
                visualizer_params["map_id"]
            )
            return StreamingResponse(data, media_type="image/png")


@router.post("/collections/{collection_uuid}/items", response_model=schemas.Item, status_code=201, responses={
    201: {
        "description": "Create collection item",
    }
})
def create_collection_item(
        collection_uuid: UUID,
        item_in: schemas.ItemCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user_or_guest),
):
    item_create = item_in.to_dto()
    item = services.create_collection_item(current_user, collection_uuid, item_create)
    return schemas.Item.from_dto(item)


@router.put("/collections/{collection_uuid}/items", response_model=schemas.ItemUpdate, status_code=201, responses={
    201: {
        "description": "Update collection items",
    }
})
def update_collection_items(
        collection_uuid: UUID,
        item_in: schemas.ItemCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user_or_guest),
):
    item_create = item_in.to_dto()
    item = services.create_collection_item(current_user, collection_uuid, item_create)
    return schemas.Item.from_dto(item)


# @router.post("/", response_model=schemas.Item)
# def create_item(
#     *,
#     db: Session = Depends(deps.get_db),
#     item_in: schemas.ItemCreate,
#     current_user: models.User = Depends(deps.get_current_active_user),
# ) -> Any:
#     """
#     Create new item.
#     """
#     item = crud.item.create_with_owner(db=db, obj_in=item_in, owner_id=current_user.id)
#     return item
#
#
# @router.put("/{id}", response_model=schemas.Item)
# def update_item(
#     *,
#     db: Session = Depends(deps.get_db),
#     id: int,
#     item_in: schemas.ItemUpdate,
#     current_user: models.User = Depends(deps.get_current_active_user),
# ) -> Any:
#     """
#     Update an item.
#     """
#     item = crud.item.get(db=db, id=id)
#     if not item:
#         raise HTTPException(status_code=404, detail="Item not found")
#     if not crud.user.is_superuser(current_user) and (item.owner_id != current_user.id):
#         raise HTTPException(status_code=400, detail="Not enough permissions")
#     item = crud.item.update(db=db, db_obj=item, obj_in=item_in)
#     return item
#
#
# @router.get("/{id}", response_model=schemas.Item)
# def read_item(
#     *,
#     db: Session = Depends(deps.get_db),
#     id: int,
#     current_user: models.User = Depends(deps.get_current_active_user),
# ) -> Any:
#     """
#     Get item by ID.
#     """
#     item = crud.item.get(db=db, id=id)
#     if not item:
#         raise HTTPException(status_code=404, detail="Item not found")
#     if not crud.user.is_superuser(current_user) and (item.owner_id != current_user.id):
#         raise HTTPException(status_code=400, detail="Not enough permissions")
#     return item
#
#
# @router.delete("/{id}", response_model=schemas.Item)
# def delete_item(
#     *,
#     db: Session = Depends(deps.get_db),
#     id: int,
#     current_user: models.User = Depends(deps.get_current_active_user),
# ) -> Any:
#     """
#     Delete an item.
#     """
#     item = crud.item.get(db=db, id=id)
#     if not item:
#         raise HTTPException(status_code=404, detail="Item not found")
#     if not crud.user.is_superuser(current_user) and (item.owner_id != current_user.id):
#         raise HTTPException(status_code=400, detail="Not enough permissions")
#     item = crud.item.remove(db=db, id=id)
#     return item

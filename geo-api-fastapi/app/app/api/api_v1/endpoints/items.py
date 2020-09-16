from enum import Enum
from typing import Any, List, Union, Optional
import logging
from fastapi import APIRouter, Depends, HTTPException, Header, Request, Query
from geoalchemy2.shape import to_shape
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.services import item
from app.api import deps

from shapely.geometry import Point
router = APIRouter()
from geojson_pydantic.features import FeatureCollection, Feature

def collection_uuid_filter(collection_uuids: Optional[str] = Query(None)):
    if not collection_uuids:
        return None

    collection_uuids_arr = collection_uuids.split(",")
    return collection_uuids_arr if len(collection_uuids_arr) > 0 else None

def transform_parameters(simplify: Optional[float] = Query(0.0)):
    return {"simplify": simplify}

def spatial_filter_parameters(spatial_filter: Optional[str] = Query(None),
                   spatial_filter_distance_x: Optional[float] = Query(None, alias="spatial_filter.distance.x"),
                   spatial_filter_distance_y: Optional[float] = Query(None, alias="spatial_filter.distance.y"),
                   spatial_filter_distance_d: Optional[float] = Query(None, alias="spatial_filter.distance.d"),
                   spatial_filter_envelope_ymin: Optional[float] = Query(None, alias="spatial_filter.envelope.ymin"),
                   spatial_filter_envelope_xmin: Optional[float] = Query(None, alias="spatial_filter.envelope.xmin"),
                   spatial_filter_envelope_ymax: Optional[float] = Query(None, alias="spatial_filter.envelope.ymax"),
                   spatial_filter_envelope_xmax: Optional[float] = Query(None, alias="spatial_filter.envelope.xmax"),
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
        elif spatial_filter in ["within", "intersect"] and (spatial_filter_envelope_ymin and spatial_filter_envelope_xmin and spatial_filter_envelope_ymax and spatial_filter_envelope_xmax):
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

@router.get("/", response_model=Union[List[schemas.Item], FeatureCollection], responses={
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
            }
        }
    }
})
def read_items(
    filter_params: dict = Depends(filter_parameters),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user_or_guest),
    accept: str = Header(None),
) -> Any:
    """
    Retrieve items.
    """

    transforms_params = {
        "simplify": 0.0
    }
    items = item.get_items(current_user, filter_params, transforms_params)
    if accept == "application/geojson":
        features = [
            Feature(geometry=to_shape(item.geometry), properties=item.properties, id=str(item.uuid))
            for item in items
            if item.geometry is not None
        ]
        return FeatureCollection(features=features)
    else:
        return items


@router.post("/", response_model=schemas.Item)
def create_item(
    *,
    db: Session = Depends(deps.get_db),
    item_in: schemas.ItemCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new item.
    """
    item = crud.item.create_with_owner(db=db, obj_in=item_in, owner_id=current_user.id)
    return item


@router.put("/{id}", response_model=schemas.Item)
def update_item(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    item_in: schemas.ItemUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an item.
    """
    item = crud.item.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not crud.user.is_superuser(current_user) and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    item = crud.item.update(db=db, db_obj=item, obj_in=item_in)
    return item


@router.get("/{id}", response_model=schemas.Item)
def read_item(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get item by ID.
    """
    item = crud.item.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not crud.user.is_superuser(current_user) and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return item


@router.delete("/{id}", response_model=schemas.Item)
def delete_item(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an item.
    """
    item = crud.item.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not crud.user.is_superuser(current_user) and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    item = crud.item.remove(db=db, id=id)
    return item

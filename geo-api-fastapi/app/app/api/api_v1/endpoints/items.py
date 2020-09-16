from enum import Enum
from typing import Any, List, Union, Optional
import logging
from fastapi import APIRouter, Depends, HTTPException, Header, Request, Query
from geoalchemy2.shape import to_shape
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.services import item
from app.api import deps

router = APIRouter()
from geojson_pydantic.features import FeatureCollection, Feature


def filter_parameters(offset: Optional[int] = Query(0),
                      limit: Optional[int] = Query(20),
                      property_filter: Optional[str] = Query(None),
                      valid: Optional[bool] = Query(False),
                      ):
    return {"offset": offset,
            "limit": limit,
            "property_filter": property_filter,
            "valid": valid,
            "spatial_filter": None,
            "collection_uuids": None,
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
async def read_items(
    filter_parameters: dict = Depends(filter_parameters),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    accept: str = Header(None),
) -> Any:
    """
    Retrieve items.
    """

    transforms_parameters = {
        "simplify": 0.0
    }
    items = item.get_items(current_user, filter_parameters, transforms_parameters)
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

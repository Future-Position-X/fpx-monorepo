from datetime import datetime
from typing import Optional
from uuid import UUID

from app.dto import ItemDTO
from geoalchemy2 import WKTElement, WKBElement
from geojson_pydantic.geometries import Geometry
from pydantic import BaseModel, validator
from shapely.geometry import mapping, Polygon, shape
from geoalchemy2.shape import to_shape
import logging


# Shared properties
class ItemBase(BaseModel):
    geometry: Optional[dict]
    properties: dict

    @validator('geometry', pre=True)
    def validate_geometry(cls, v):
        if v is None:
            return None
        if type(v) is dict:
            return v
        if type(v) is WKBElement:
            as_dict = mapping(to_shape(v))
            logging.error(type(as_dict))
            return as_dict
        elif hasattr(v, "__geo_interface__"):
            return v.__geo_interface__
        else:
            raise ValueError('can not transform geometry to dict from type ' + str(type(v)))

    class Config:
        arbitrary_types_allowed = False


# Properties to receive on item creation
class ItemCreate(ItemBase):
    def to_dto(self):
        return ItemDTO(**{
            "geometry": shape(self.geometry).to_wkt(),
            "properties": self.properties
        })


# Properties to receive on item update
class ItemUpdate(ItemBase):
    uuid: UUID

    def to_dto(self):
        return ItemDTO(**{
            "uuid": self.uuid,
            "geometry": shape(self.geometry).to_wkt(),
            "properties": self.properties
        })


# Properties shared by models stored in DB
class ItemInDBBase(ItemBase):
    uuid: UUID
    collection_uuid: UUID
    created_at: datetime
    updated_at: datetime
    revision: int

    class Config:
        orm_mode = True


# Properties to return to client
class Item(ItemInDBBase):
    @classmethod
    def from_dto(cls, dto):
        return cls(
            uuid=dto.uuid,
            collection_uuid=dto.collection_uuid,
            geometry=dto.geometry,
            properties=dto.properties,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
            revision=dto.revision
        )


# Properties properties stored in DB
class ItemInDB(ItemInDBBase):
    pass

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional, Type
from uuid import UUID

from geoalchemy2 import WKBElement, WKTElement
from geoalchemy2.shape import to_shape
from pydantic import BaseModel, validator
from shapely.geometry import mapping, shape

from app.dto import ItemDTO


# Shared properties
class ItemBase(BaseModel):
    geometry: Optional[dict]
    properties: dict

    @validator("geometry", pre=True)
    def validate_geometry(cls, v: Any) -> Optional[dict]:
        if v is None:
            return None
        if type(v) is dict:
            return v
        if type(v) is str:
            as_dict = mapping(to_shape(WKTElement(v)))
            return as_dict
        if type(v) is WKBElement:
            as_dict = mapping(to_shape(v))
            return as_dict
        elif hasattr(v, "__geo_interface__"):
            return v.__geo_interface__
        else:
            raise ValueError(
                "can not transform geometry to dict from type " + str(type(v))
            )

    class Config:
        arbitrary_types_allowed = False


# Properties to receive on item creation
class ItemCreate(ItemBase):
    def to_dto(self) -> ItemDTO:
        geometry = None
        if self.geometry is not None:
            geometry = shape(self.geometry).to_wkt()
        return ItemDTO(**{"geometry": geometry, "properties": self.properties})


# Properties to receive on item update
class ItemUpdate(ItemBase):
    def to_dto(self) -> ItemDTO:
        return ItemDTO(
            **{"geometry": shape(self.geometry).to_wkt(), "properties": self.properties}
        )


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
    def from_dto(cls: Type, dto: ItemDTO) -> Item:
        return cls(
            uuid=dto.uuid,
            collection_uuid=dto.collection_uuid,
            geometry=dto.geometry,
            properties=dto.properties,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
            revision=dto.revision,
        )


# Properties properties stored in DB
class ItemInDB(ItemInDBBase):
    pass

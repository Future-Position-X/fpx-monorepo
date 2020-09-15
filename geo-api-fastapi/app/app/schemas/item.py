from datetime import datetime
from typing import Optional
from uuid import UUID

from geoalchemy2 import WKTElement, WKBElement
from pydantic import BaseModel, validator
from shapely.geometry import mapping
from geoalchemy2.shape import to_shape
import logging

# Shared properties
class ItemBase(BaseModel):
    collection_uuid: UUID
    geometry: dict
    properties: dict

    @validator('geometry', pre=True)
    def is_WKBElement(cls, v):
        logging.error("WTF")
        logging.error(type(v))
        if type(v) is WKBElement:
            as_dict = mapping(to_shape(v))
            logging.error(type(as_dict))
            return as_dict
        else:
            raise ValueError('geometry is not WKTElement')

    class Config:
        arbitrary_types_allowed = False

# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    pass


# Properties shared by models stored in DB
class ItemInDBBase(ItemBase):
    uuid: UUID
    created_at: datetime
    updated_at: datetime
    revision: int

    class Config:
        orm_mode = True


# Properties to return to client
class Item(ItemInDBBase):
    pass

# Properties properties stored in DB
class ItemInDB(ItemInDBBase):
    pass

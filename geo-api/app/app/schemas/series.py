from __future__ import annotations

from datetime import datetime
from typing import Type
from uuid import UUID

from pydantic import BaseModel

from app.dto import SeriesDTO


# Shared properties
class SeriesBase(BaseModel):
    data: dict

    class Config:
        arbitrary_types_allowed = False


class SeriesCreate(SeriesBase):
    def to_dto(self) -> SeriesDTO:
        return SeriesDTO(**{"data": self.data})


class SeriesUpdate(SeriesBase):
    def to_dto(self) -> SeriesDTO:
        return SeriesDTO(**{"data": self.data})


class SeriesInDBBase(SeriesBase):
    uuid: UUID
    item_uuid: UUID
    created_at: datetime
    updated_at: datetime
    revision: int

    class Config:
        orm_mode = True


class Series(SeriesInDBBase):
    @classmethod
    def from_dto(cls: Type, dto: SeriesDTO) -> Series:
        return cls(
            uuid=dto.uuid,
            item_uuid=dto.item_uuid,
            data=dto.data,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
            revision=dto.revision,
        )


class SeriesInDB(SeriesInDBBase):
    pass

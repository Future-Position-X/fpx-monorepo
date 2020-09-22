from datetime import datetime
from typing import Optional
from uuid import UUID

from app.dto import ACLDTO, CollectionDTO
from pydantic import BaseModel


class CollectionBase(BaseModel):
    name: str
    is_public: bool


class CollectionCreate(CollectionBase):
    def to_dto(self) -> CollectionDTO:
        return CollectionDTO(**{
            "name": self.name,
            "is_public": self.is_public,
        })


class CollectionUpdate(CollectionBase):
    pass


# Properties shared by models stored in DB
class CollectionInDBBase(CollectionBase):
    uuid: UUID
    provider_uuid: UUID
    created_at: datetime
    updated_at: datetime
    revision: int

    class Config:
        orm_mode = True


class Collection(CollectionInDBBase):
    @classmethod
    def from_dto(cls, dto: CollectionDTO):
        return cls(
            uuid=dto.uuid,
            provider_uuid=dto.provider_uuid,
            name=dto.name,
            is_public=dto.is_public,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
            revision=dto.revision
        )


class CollectionInDB(CollectionInDBBase):
    pass

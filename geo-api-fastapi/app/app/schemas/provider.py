from datetime import datetime
from typing import Type
from uuid import UUID

from pydantic import BaseModel

from app.dto import ProviderDTO


class ProviderBase(BaseModel):
    name: str

    def to_dto(self) -> ProviderDTO:
        return ProviderDTO(**{"name": self.name})


class ProviderCreate(ProviderBase):
    pass


class ProviderUpdate(ProviderBase):
    pass


# Properties shared by models stored in DB
class ProviderInDBBase(ProviderBase):
    uuid: UUID
    created_at: datetime
    updated_at: datetime
    revision: int

    class Config:
        orm_mode = True


class Provider(ProviderInDBBase):
    @classmethod
    def from_dto(cls, dto: ProviderDTO) -> Provider:
        return cls(
            uuid=dto.uuid,
            name=dto.name,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
            revision=dto.revision,
        )


class ProviderInDB(ProviderInDBBase):
    pass

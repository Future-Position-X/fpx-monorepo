from datetime import datetime
from typing import Optional
from uuid import UUID

from app.dto import ACLDTO
from pydantic import BaseModel


class ACLBase(BaseModel):
    granted_provider_uuid: Optional[UUID]
    granted_user_uuid: Optional[UUID]
    collection_uuid: Optional[UUID]
    item_uuid: Optional[UUID]
    access: str = None


class ACLCreate(ACLBase):
    def to_dto(self) -> ACLDTO:
        return ACLDTO(**{
            "granted_provider_uuid": self.granted_provider_uuid,
            "granted_user_uuid": self.granted_user_uuid,
            "collection_uuid": self.collection_uuid,
            "item_uuid": self.item_uuid,
            "access": self.access,
        })


class ACLUpdate(ACLBase):
    pass


# Properties shared by models stored in DB
class ACLInDBBase(ACLBase):
    uuid: UUID
    provider_uuid: UUID
    created_at: datetime
    updated_at: datetime
    revision: int

    class Config:
        orm_mode = True


class ACL(ACLInDBBase):
    @classmethod
    def from_dto(cls, dto: ACLDTO):
        return cls(
            uuid=dto.uuid,
            provider_uuid=dto.provider_uuid,
            granted_provider_uuid=dto.granted_provider_uuid,
            granted_user_uuid=dto.granted_user_uuid,
            collection_uuid=dto.collection_uuid,
            item_uuid=dto.item_uuid,
            access=dto.access,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
            revision=dto.revision
        )


class ACLInDB(ACLInDBBase):
    pass

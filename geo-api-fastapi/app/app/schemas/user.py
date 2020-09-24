from datetime import datetime
from typing import Optional
from uuid import UUID

from app.dto import UserDTO
from pydantic import BaseModel, EmailStr


# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str

    def to_dto(self) -> UserDTO:
        return UserDTO(**{
            "email": self.email,
            "password": self.password,
        })


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None

    def to_dto(self) -> UserDTO:
        return UserDTO(**{
            "email": self.email,
            "password": self.password,
        })


class UserInDBBase(UserBase):
    uuid: UUID
    provider_uuid: UUID
    created_at: datetime
    updated_at: datetime
    revision: int

    class Config:
        orm_mode = True

    def to_dto(self) -> UserDTO:
        return UserDTO(**{
            "uuid": self.uuid,
            "email": self.email,
            "provider_uuid": self.provider_uuid,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "revision": self.revision,
        })

# Additional properties to return via API
class User(UserInDBBase):
    @classmethod
    def from_dto(cls, dto: UserDTO):
        return cls(
            uuid=dto.uuid,
            provider_uuid=dto.provider_uuid,
            email=dto.email,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
            revision=dto.revision
        )


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    password: str
    @classmethod

    def from_dto(cls, dto: UserDTO):
        return cls(
            uuid=dto.uuid,
            provider_uuid=dto.provider_uuid,
            email=dto.email,
            password=dto.password,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
            revision=dto.revision
        )

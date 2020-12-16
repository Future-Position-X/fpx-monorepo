from datetime import datetime
from enum import Enum
from typing import Any, List, Optional
from uuid import UUID

from geoalchemy2 import WKTElement


class BaseDTO:
    __slots__: List[str] = []

    def __init__(self, kwargs: Any, slots: List[str]):
        self.add_slots(slots)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def add_slots(self, slots: List[str]) -> None:
        self.__slots__ = self.__slots__ + slots

    def to_dict(self) -> dict:
        attrs = {}
        for att in self.__slots__:
            if hasattr(self, att):
                attrs[att] = getattr(self, att)
        return attrs


class BaseModelDTO(BaseDTO):
    uuid: UUID
    created_at: datetime
    updated_at: datetime
    revision: int
    __slots__ = ["uuid", "created_at", "updated_at", "revision"]


class CollectionDTO(BaseModelDTO):
    provider_uuid: UUID
    name: str
    is_public: bool

    def __init__(self, **kwargs: Any):
        super().__init__(kwargs, ["provider_uuid", "name", "is_public"])


class ItemDTO(BaseModelDTO):
    collection_uuid: UUID
    geometry: WKTElement
    properties: dict

    def __init__(self, **kwargs: Any):
        super().__init__(kwargs, ["collection_uuid", "geometry", "properties"])


class ProviderDTO(BaseModelDTO):
    name: str

    def __init__(self, **kwargs: Any):
        super().__init__(kwargs, ["name"])


class UserDTO(BaseModelDTO):
    provider_uuid: UUID
    email: str
    password: str

    def __init__(self, **kwargs: Any):
        super().__init__(kwargs, ["provider_uuid", "email", "password"])


class ACLDTO(BaseModelDTO):
    provider_uuid: UUID
    granted_provider_uuid: Optional[UUID] = None
    granted_user_uuid: Optional[UUID] = None
    collection_uuid: Optional[UUID] = None
    item_uuid: Optional[UUID] = None
    access: str

    def __init__(self, **kwargs: Any):
        super().__init__(
            kwargs,
            [
                "provider_uuid",
                "granted_provider_uuid",
                "granted_user_uuid",
                "collection_uuid",
                "item_uuid",
                "access",
            ],
        )


class NoValue(Enum):
    def __repr__(self) -> str:
        return "<%s.%s>" % (self.__class__.__name__, self.name)


class Access(NoValue):
    READ = "read"
    WRITE = "write"


class InternalUserDTO(BaseDTO):
    uuid: UUID
    provider_uuid: UUID

    def __init__(self, **kwargs: Any):
        super().__init__(kwargs, ["uuid", "provider_uuid"])


class SeriesDTO(BaseModelDTO):
    item_uuid: UUID
    data: dict

    def __init__(self, **kwargs: Any):
        super().__init__(kwargs, ["item_uuid", "data"])


class MetricDTO(BaseModelDTO):
    ts: datetime
    series_uuid: UUID
    data: dict

    def __init__(self, **kwargs: Any):
        super().__init__(kwargs, ["series_uuid", "data"])

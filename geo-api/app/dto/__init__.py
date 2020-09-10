from uuid import UUID
from enum import Enum
from geoalchemy2 import WKTElement


class BaseDTO:
    __slots__ = []

    def __init__(self, kwargs, slots):
        self.add_slots(slots)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def add_slots(self, slots):
        self.__slots__ = self.__slots__ + slots

    def to_dict(self):
        attrs = {}
        for att in self.__slots__:
            if hasattr(self, att):
                attrs[att] = getattr(self, att)
        return attrs


class BaseModelDTO(BaseDTO):
    __slots__ = ["uuid", "created_at", "updated_at", "revision"]


class CollectionDTO(BaseModelDTO):
    provider_uuid: UUID
    name: str
    is_public: bool

    def __init__(self, **kwargs):
        super().__init__(kwargs, ["provider_uuid", "name", "is_public"])


class ItemDTO(BaseModelDTO):
    collection_uuid: UUID
    geometry: WKTElement
    properties: dict

    def __init__(self, **kwargs):
        super().__init__(kwargs, ["collection_uuid", "geometry", "properties"])


class ProviderDTO(BaseModelDTO):
    def __init__(self, **kwargs):
        super().__init__(kwargs, ["name"])


class UserDTO(BaseModelDTO):
    def __init__(self, **kwargs):
        super().__init__(kwargs, ["provider_uuid", "email", "password"])


class ACLDTO(BaseModelDTO):
    provider_uuid: UUID = None
    granted_provider_uuid: UUID = None
    granted_user_uuid: UUID = None
    collection_uuid: UUID = None
    item_uuid: UUID = None
    access: str = None

    def __init__(self, **kwargs):
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
    def __repr__(self):
        return "<%s.%s>" % (self.__class__.__name__, self.name)


class Access(NoValue):
    READ = "read"
    WRITE = "write"


class InternalUserDTO(BaseDTO):
    uuid: UUID
    provider_uuid: UUID

    def __init__(self, **kwargs):
        super().__init__(kwargs, ["uuid", "provider_uuid"])

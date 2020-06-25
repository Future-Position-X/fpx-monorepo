class BaseModelDTO:
    __slots__ = ['uuid',
                 'created_at', 'updated_at', 'revision']

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


class CollectionDTO(BaseModelDTO):

    def __init__(self, **kwargs):
        super().__init__(kwargs, ['provider_uuid', 'name', 'is_public'])


class ItemDTO(BaseModelDTO):

    def __init__(self, **kwargs):
        super().__init__(kwargs, ['collection_uuid', 'geometry', 'properties'])


class ProviderDTO(BaseModelDTO):

    def __init__(self, **kwargs):
        super().__init__(kwargs, ['name'])


class UserDTO(BaseModelDTO):

    def __init__(self, **kwargs):
        super().__init__(kwargs, ['provider_uuid', 'email', 'password'])
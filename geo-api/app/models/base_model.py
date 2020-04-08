class BaseModel():
    __slots__ = ['uuid', 'provider_uuid',
                 'created_at', 'updated_at', 'revision']

    def __init__(self, kwargs, slots):
        self.add_slots(slots)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def add_slots(self, slots):
        self.__slots__ = self.__slots__ + slots

    def as_dict(self):
        attrs = {}
        for att in self.__slots__:
            if hasattr(self, att):
                attrs[att] = getattr(self, att)
        return attrs

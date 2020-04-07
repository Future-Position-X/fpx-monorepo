import rapidjson
from rapidjson import DM_ISO8601

class Collection(object):
    __slots__ = ['uuid', 'provider_uuid', 'name',
                 'created_at', 'updated_at', 'revision', 'is_public']
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def as_dict(self):
        attrs = {}
        for att in self.__slots__:
            attrs[att] = getattr(self, att)
        return attrs

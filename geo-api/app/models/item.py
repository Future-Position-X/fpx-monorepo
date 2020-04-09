from app.models.base_model import BaseModel


class Item(BaseModel, object):

    def __init__(self, **kwargs):
        super().__init__(kwargs, ['collection_uuid', 'geometry', 'properties'])

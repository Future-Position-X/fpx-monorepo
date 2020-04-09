from app.models.base_model import BaseModel


class Collection(BaseModel, object):

    def __init__(self, **kwargs):
        super().__init__(kwargs, ['name', 'is_public'])

from app.models.base_model import BaseModel


class Provider(BaseModel, object):

    def __init__(self, **kwargs):
        super().__init__(kwargs, ['name '])

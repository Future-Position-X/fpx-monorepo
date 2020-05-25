from app.models.base_model import BaseModel


class User(BaseModel, object):

    def __init__(self, **kwargs):
        super().__init__(kwargs, ['email', 'password'])

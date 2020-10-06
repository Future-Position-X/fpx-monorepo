from pydantic.main import BaseModel


class SessionCreate(BaseModel):
    email: str
    password: str

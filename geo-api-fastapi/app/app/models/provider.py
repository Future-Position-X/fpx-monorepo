from sqlalchemy.dialects.postgresql import UUID


from app.models import BaseModel
import sqlalchemy as sa
from sqlalchemy.orm import relationship
class Provider(BaseModel):
    __tablename__ = "providers"

    uuid = sa.Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
        unique=True,
        nullable=False,
    )
    name = sa.Column(sa.Text(), unique=True)

    collections = relationship("Collection", backref="provider", lazy=True)

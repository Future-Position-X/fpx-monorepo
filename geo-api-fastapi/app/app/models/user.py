import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from app.models.base_model import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    uuid = sa.Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
        unique=True,
        nullable=False,
    )
    email = sa.Column(sa.Text(), unique=True)
    password = sa.Column(sa.Text(), nullable=False)

    provider_uuid = sa.Column(
        UUID(as_uuid=True), sa.ForeignKey("providers.uuid"), index=True, nullable=False
    )

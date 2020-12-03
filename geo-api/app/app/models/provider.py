from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from .collection import Collection  # noqa: F401


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

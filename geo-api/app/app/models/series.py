from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import relationship

from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from .item import Item  # noqa: F401


class Series(BaseModel):
    __tablename__ = "series"
    uuid = sa.Column(
        pg.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    item_uuid = sa.Column(
        pg.UUID(as_uuid=True), sa.ForeignKey("items.uuid"), index=True, nullable=False,
    )
    data = sa.Column(pg.JSONB)

    items = relationship("Item", lazy=True, viewonly=True)

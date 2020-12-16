from __future__ import annotations

import uuid
from uuid import UUID
from typing import TYPE_CHECKING, List

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import relationship

from app.models.base_model import BaseModel
from ..dto import SeriesDTO

if TYPE_CHECKING:
    from .item import Item  # noqa: F401
    from .metric import Metric  # noqa: F401


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

    item = relationship("Item")
    metrics = relationship("Metric", lazy=True, viewonly=True)

    @classmethod
    def find_by_item_uuid(cls, item_uuid: UUID,) -> List[SeriesDTO]:
        query = cls.query.filter(cls.item_uuid == item_uuid)
        res = query.all()
        return res

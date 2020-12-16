from __future__ import annotations

from typing import List, TYPE_CHECKING
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import relationship

from app.dto import SeriesDTO
from app.models.base_model import BaseModel


if TYPE_CHECKING:
    from .series import Series  # noqa: F401


class Metric(BaseModel):
    __tablename__ = "metrics"
    __table_args__ = (sa.PrimaryKeyConstraint("series_uuid", "ts"),)
    ts = sa.Column(sa.DateTime, server_default=sa.text("now()"), nullable=False)
    series_uuid = sa.Column(
        pg.UUID(as_uuid=True), sa.ForeignKey("series.uuid"), index=True, nullable=False,
    )
    data = sa.Column(pg.JSONB)

    series = relationship("Series")

    @classmethod
    def find_by_series_uuid(cls, series_uuid: UUID,) -> List[SeriesDTO]:
        query = cls.query.filter(cls.series_uuid == series_uuid)
        res = query.all()
        return res

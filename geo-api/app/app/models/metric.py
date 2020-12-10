from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import relationship

from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from .item import Item  # noqa: F401


class Metric(BaseModel):
    __tablename__ = "metrics"
    __table_args__ = (sa.PrimaryKeyConstraint("series_uuid", "ts"),)
    ts = sa.Column(sa.DateTime, server_default=sa.text("now()"), nullable=False)
    series_uuid = sa.Column(
        pg.UUID(as_uuid=True),
        sa.ForeignKey("timeseries.uuid"),
        index=True,
        nullable=False,
    )
    data = sa.Column(pg.JSONB)

    timeseries = relationship("timeseries")

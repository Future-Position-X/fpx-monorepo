from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

import sqlalchemy as sa
import sqlalchemy_mixins
from geoalchemy2 import Geometry
from sqlalchemy import Column, and_, func, or_
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import Query, relationship

from app.dto import Access, InternalUserDTO, ItemDTO
from app.models import Collection
from app.models.acl import ACL
from app.models.base_model import BaseModel


class Metric(BaseModel):
    __tablename__ = "metrics"
    __table_args__ = (sa.PrimaryKeyConstraint("series_uuid", "ts"),)
    ts = sa.Column(sa.DateTime, server_default=sa.text("now()"), nullable=False)
    series_uuid = sa.Column(
        pg.UUID(as_uuid=True), sa.ForeignKey("series.uuid"), index=True, nullable=False,
    )
    data = sa.Column(pg.JSONB)

    series = relationship("Series")

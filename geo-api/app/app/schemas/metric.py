from __future__ import annotations

from datetime import datetime
from typing import Type
from uuid import UUID

from pydantic import BaseModel
from app.dto import MetricDTO


# Shared properties
class MetricBase(BaseModel):
    ts: datetime
    data: dict

    class Config:
        arbitrary_types_allowed = False


class MetricCreate(MetricBase):
    def to_dto(self) -> MetricDTO:
        return MetricDTO(**{"ts": self.ts, "data": self.data})


class MetricUpdate(MetricBase):
    def to_dto(self) -> MetricDTO:
        return MetricDTO(**{"data": self.data})


class MetricInDBBase(MetricBase):
    series_uuid: UUID
    created_at: datetime
    updated_at: datetime
    revision: int

    class Config:
        orm_mode = True


class Metric(MetricInDBBase):
    @classmethod
    def from_dto(cls: Type, dto: MetricDTO) -> Metric:
        return cls(
            ts=dto.ts,
            series_uuid=dto.series_uuid,
            data=dto.data,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
            revision=dto.revision,
        )


class MetricInDB(MetricInDBBase):
    pass

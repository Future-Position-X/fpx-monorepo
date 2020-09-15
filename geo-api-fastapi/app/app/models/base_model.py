import uuid
from typing import List, Type, TypeVar
from app.dto import BaseModelDTO, ItemDTO, InternalUserDTO, Access
import sqlalchemy_mixins
from shapely_geojson import Feature as BaseFeature

from sqlalchemy_mixins import (
    ActiveRecordMixin,
    SmartQueryMixin,
    ReprMixin,
    SerializeMixin,
    ModelNotFoundError,
)
from sqlalchemy import func, or_, and_
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
Base = declarative_base()

class Feature(BaseFeature):
    def __init__(self, geometry, properties=None, id=None):
        self.geometry = geometry
        self.properties = properties
        self.id = id

    @property
    def __geo_interface__(self):
        if self.id is not None:
            return {
                "id": self.id,
                "type": "Feature",
                "geometry": self.geometry.__geo_interface__,
                "properties": self.properties,
            }
        else:
            return {
                "type": "Feature",
                "geometry": self.geometry.__geo_interface__,
                "properties": self.properties,
            }


class FPXActiveRecordMixin(ActiveRecordMixin, SmartQueryMixin):
    __abstract__ = True

    @classmethod
    def first_or_fail(cls, **kwargs):
        result = cls.where(**kwargs).first()
        if result:
            return result
        else:
            raise ModelNotFoundError(
                "{} with matching '{}' was not found".format(cls.__name__, kwargs)
            )


class FPXTimestampsMixin:
    __abstract__ = True

    __datetime_callback__ = sa.func.now

    created_at = sa.Column(sa.DateTime, server_default=sa.text("now()"), nullable=False)

    updated_at = sa.Column(sa.DateTime, server_default=sa.text("now()"), nullable=False)


@sa.event.listens_for(FPXTimestampsMixin, "before_update", propagate=True)
def _receive_before_update(mapper, connection, target):
    """Listen for updates and update `updated_at` column."""
    target.updated_at = target.__datetime_callback__()


class BaseModel(
    Base,
    FPXActiveRecordMixin,
    SmartQueryMixin,
    ReprMixin,
    SerializeMixin,
    FPXTimestampsMixin,
):
    __abstract__ = True

    revision = sa.Column(sa.Integer, server_default=sa.text("1"), nullable=False)

    __mapper_args__ = {"version_id_col": revision}

    pass


BDTO = TypeVar("BDTO", bound=BaseModelDTO)
BM = TypeVar("BM", bound=BaseModel)


def to_model(db_model: BM, klass: Type[BDTO]) -> BDTO:
    return klass(**db_model.to_dict())


def to_models(db_models: List[BM], klass: Type[BDTO]) -> List[BDTO]:
    return [to_model(db_model, klass) for db_model in db_models]

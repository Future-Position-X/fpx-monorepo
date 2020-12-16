from typing import Any, List, Type, TypeVar

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_mixins import (
    ActiveRecordMixin,
    ModelNotFoundError,
    ReprMixin,
    SerializeMixin,
    SmartQueryMixin,
)

from app.dto import BaseModelDTO

Base = declarative_base()
T = TypeVar("T")


class FPXActiveRecordMixin(ActiveRecordMixin, SmartQueryMixin):
    __abstract__ = True

    @classmethod
    def first(cls, **kwargs: Any) -> T:
        result = cls.where(**kwargs).first()
        return result

    @classmethod
    def first_or_fail(cls, **kwargs: Any) -> T:
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
def _receive_before_update(mapper: Any, connection: Any, target: Any) -> None:
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


BDTO = TypeVar("BDTO", bound=BaseModelDTO)
BM = TypeVar("BM", bound=BaseModel)


def to_model(db_model: BM, klass: Type[BDTO]) -> BDTO:
    return klass(**db_model.to_dict())


def to_models(db_models: List[BM], klass: Type[BDTO]) -> List[BDTO]:
    return [to_model(db_model, klass) for db_model in db_models]

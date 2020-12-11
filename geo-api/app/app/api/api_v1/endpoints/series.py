from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends

from app import models, schemas, services
from app.api import deps

router = APIRouter()


@router.post(
    "/items/{item_uuid}/series",
    # response_model=schemas.Series,
    # response_model_exclude_none=True,
    status_code=201,
)
def create_item_series(
    item_uuid: UUID,
    series_create: schemas.SeriesCreate,
    current_user: models.User = Depends(deps.get_current_user),
) -> schemas.Series:
    series = services.series.create_item_series(current_user, item_uuid, series_create.to_dto())
    return schemas.Series.from_dto(series)


@router.get(
    "/items/{item_uuid}/series",
    status_code=201
)
def get_item_series(
    item_uuid: UUID,
    current_user: models.User = Depends(deps.get_current_user_or_guest),
) -> List[schemas.Series]:
    series = services.series.get_item_series(current_user, item_uuid)
    return [schemas.Series.from_dto(s) for s in series]
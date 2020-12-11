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

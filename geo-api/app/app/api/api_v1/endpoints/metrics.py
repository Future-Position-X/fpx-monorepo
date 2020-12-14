from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends

from app import models, schemas, services
from app.api import deps

router = APIRouter()


@router.post(
    "/series/{series_uuid}/metrics",
    # response_model=schemas.Series,
    # response_model_exclude_none=True,
    status_code=201,
)
def create_series_metric(
    series_uuid: UUID,
    metric_create: schemas.MetricCreate,
    current_user: models.User = Depends(deps.get_current_user),
) -> schemas.Metric:
    series = services.metric.create_series_metric(current_user, series_uuid, metric_create.to_dto())
    return schemas.Metric.from_dto(series)


@router.get(
    "/series/{series_uuid}/metrics",
    status_code=200
)
def get_series_metrics(
    series_uuid: UUID,
    current_user: models.User = Depends(deps.get_current_user_or_guest),
) -> List[schemas.Metric]:
    metrics = services.metric.get_series_metrics(current_user, series_uuid)
    return [schemas.Metric.from_dto(m) for m in metrics]
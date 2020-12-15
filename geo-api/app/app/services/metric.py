from typing import List
from uuid import UUID

from app.dto import InternalUserDTO, MetricDTO
from app.models import Item, Metric, Series
from app.models.base_model import to_model, to_models


def create_series_metric(
    user: InternalUserDTO, series_uuid: UUID, metric_dto: MetricDTO
) -> MetricDTO:
    series = Series.find_or_fail(series_uuid)
    item = Item.find_writeable_or_fail(user, series.item_uuid)
    metric_dto.series_uuid = series.uuid  # type: ignore
    metric = Metric(**metric_dto.to_dict())
    metric.save()
    metric.session.commit()
    return to_model(metric, MetricDTO)


def get_series_metrics(
    user: InternalUserDTO, series_uuid: UUID
) -> List[MetricDTO]:
    series = Series.find_or_fail(series_uuid)
    Item.find_readable_or_fail(user, series.item_uuid)
    metrics_dtos = Metric.find_by_series_uuid(series.uuid)
    metrics = [Metric(**m.to_dict()) for m in metrics_dtos]
    return to_models(metrics, MetricDTO)
from uuid import UUID

from app.dto import InternalUserDTO, SeriesDTO
from app.models import Item, Series
from app.models.base_model import to_model, to_models


def create_item_series(
    user: InternalUserDTO, item_uuid: UUID, series_dto: SeriesDTO
) -> SeriesDTO:
    item = Item.find_writeable_or_fail(user, item_uuid)
    series_dto.item_uuid = item.uuid  # type: ignore
    series = Series(**series_dto.to_dict())
    series.save()
    series.session.commit()
    return to_model(series, SeriesDTO)


def get_item_series(
    user: InternalUserDTO, item_uuid: UUID
) -> SeriesDTO:
    item = Item.find_readable_or_fail(user, item_uuid)
    series_dtos = Series.find_by_item_uuid(item.uuid)
    series = [Series(**s.to_dict()) for s in series_dtos]
    return to_models(series, SeriesDTO)

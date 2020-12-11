from uuid import UUID

from app.dto import InternalUserDTO, SeriesDTO
from app.models import Item, Series
from app.models.base_model import to_model


def create_item_series(
    user: InternalUserDTO, item_uuid: UUID, series_dto: SeriesDTO
) -> SeriesDTO:
    item = Item.find_writeable_or_fail(user, item_uuid)
    series_dto.item_uuid = item.uuid  # type: ignore
    series = Series(**series_dto.to_dict())
    series.save()
    series.session.commit()
    return to_model(series, SeriesDTO)

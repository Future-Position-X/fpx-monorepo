from fastapi import APIRouter, Depends

from app import models, services
from app.api import deps
from app.api.api_v1.endpoints.items import filter_parameters, spatial_filter_parameters

router = APIRouter()


@router.get("/health", status_code=200)
def get_health(
    current_user: models.User = Depends(deps.get_current_user_or_guest),
) -> str:
    spatial_filter = spatial_filter_parameters(
        spatial_filter="intersect",
        spatial_filter_envelope_xmin=16.91514624249102,
        spatial_filter_envelope_ymin=60.54014515251819,
        spatial_filter_envelope_xmax=17.095304857603324,
        spatial_filter_envelope_ymax=60.60643551894273,
    )
    filter_params = filter_parameters(
        offset=0,
        limit=5,
        valid=False,
        spatial_filter=spatial_filter,
        property_filter=None,
        collection_uuids=None,
    )
    items = services.item.get_collection_items_by_name(
        current_user, "deso", filter_params, {"simplify": 0.5}
    )
    assert len(items) >= 1
    return "healthy!"

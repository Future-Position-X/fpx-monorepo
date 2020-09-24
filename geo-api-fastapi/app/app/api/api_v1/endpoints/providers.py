from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends

from app import schemas, models, services
from app.api import deps

router = APIRouter()


@router.get("/providers")
def get_providers() -> List[schemas.Provider]:
    providers = services.provider.get_providers()
    return [schemas.Provider.from_dto(provider) for provider in providers]


@router.get("/providers/{provider_uuid}")
def get_provider(
        provider_uuid: UUID,
) -> schemas.Provider:
    provider = services.provider.get_provider(provider_uuid)
    return schemas.Provider.from_dto(provider)


@router.put("/providers/{provider_uuid}", status_code=204)
def update_provider(
        provider_uuid: UUID,
        provider_in: schemas.ProviderUpdate,
        current_user: models.User = Depends(deps.get_current_user),
) -> None:
    if current_user.provider_uuid != provider_uuid:
        raise PermissionError
    services.provider.update_provider(provider_uuid, provider_in.to_dto())
    return None

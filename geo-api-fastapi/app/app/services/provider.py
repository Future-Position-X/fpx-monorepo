from typing import List
from uuid import UUID

from app.dto import ProviderDTO
from app.models import Provider
from app.models.base_model import to_models, to_model


def get_providers() -> List[ProviderDTO]:
    providers = Provider.all()
    return to_models(providers, ProviderDTO)


def get_provider(provider_uuid: UUID) -> ProviderDTO:
    provider = Provider.find_or_fail(provider_uuid)
    return to_model(provider, ProviderDTO)


def update_provider(provider_uuid: UUID, provider_update: ProviderDTO) -> ProviderDTO:
    provider = Provider.find_or_fail(provider_uuid)
    provider.name = provider_update.name
    provider.save()
    provider.session.commit()
    return to_model(provider, ProviderDTO)


def create_provider(provider: ProviderDTO) -> ProviderDTO:
    provider = Provider(**provider.to_dict())
    provider.save()
    provider.session.commit()
    return to_model(provider, ProviderDTO)

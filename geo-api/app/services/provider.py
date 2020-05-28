from app.stores.provider import ProviderStore
from app.stores import DB

def create_provider(provider):
    with DB().transaction():
        uuid = ProviderStore.insert(provider)
        return uuid


def get_all_providers():
    with ProviderStore() as provider_store:
        providers = provider_store.find_all()
        provider_store.complete()
        return providers


def get_provider_by_uuid(provider_uuid):
    with ProviderStore() as provider_store:
        provider = provider_store.get_by_uuid(provider_uuid)
        provider_store.complete()
        return provider


def update_provider_by_uuid(provider_uuid, provider):
    with ProviderStore() as provider_store:
        provider_store.update(provider_uuid, provider)
        provider_store.complete()

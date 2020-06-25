from app.stores.user import UserStore
from app.stores import DB
from app.services.provider import create_provider
from app.dto import ProviderDTO


def create_user(user):
    with DB().transaction():
        provider_uuid = create_provider(ProviderDTO(**{"name": user.email}))
        user.provider_uuid = provider_uuid
        uuid = UserStore.insert(user)
        return uuid


def get_user_by_uuid(user_uuid):
    with UserStore() as user_store:
        user = user_store.get_by_uuid(user_uuid)
        user_store.complete()
        return user


def get_user_by_email(email):
    with UserStore() as user_store:
        user = user_store.get_by_email(email)
        user_store.complete()
        return user


def update_user_by_uuid(user_uuid, user):
    with UserStore() as user_store:
        user_store.update(user_uuid, user)
        user_store.complete()


def delete_user_by_uuid(user_uuid):
    with UserStore() as user_store:
        user_store.delete(user_uuid)
        user_store.complete()
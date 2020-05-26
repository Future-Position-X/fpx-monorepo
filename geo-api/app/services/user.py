from app.stores.user import UserStore
from app.services.provider import create_provider
from app.models.provider import Provider


def create_user(user):
    with UserStore() as user_store:
        provider = Provider({"name": user.email})
        provider_uuid = create_provider(provider)
        user.provider_uuid = provider_uuid
        uuid = user_store.insert(user)
        user_store.complete()
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

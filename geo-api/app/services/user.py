from app.stores.user import UserStore
from app.models.user import User

def create_user(user):
    with UserStore() as user_store:
        uuid = user_store.insert(user)
        user_store.complete()
        return uuid


def get_user_by_uuid(user_uuid):
    with UserStore() as user_store:
        user = user_store.get_by_uuid(user_uuid)
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
from app.stores.collection import CollectionStore
from app.services.item import copy_items_by_collection_uuid
from app.models.collection import Collection

def create_collection(collection):
    with CollectionStore() as collection_store:
        uuid = collection_store.insert(collection)
        collection_store.complete()
        return uuid


def get_all_collections():
    with CollectionStore() as collection_store:
        collections = collection_store.find_all()
        collection_store.complete()
        return collections


def get_collection_by_uuid(collection_uuid):
    with CollectionStore() as collection_store:
        collection = collection_store.get_by_uuid(collection_uuid)
        collection_store.complete()
        return collection


def get_collection_uuid_by_collection_name(collection_name):
    with CollectionStore() as collection_store:
        uuid = collection_store.get_uuid_by_name(collection_name)
        collection_store.complete()
        return uuid


def delete_collection_by_uuid(collection_uuid):
    with CollectionStore() as collection_store:
        collection_store.delete(collection_uuid)
        collection_store.complete()


def update_collection_by_uuid(collection_uuid, collection):
    with CollectionStore() as collection_store:
        collection_store.update(collection_uuid, collection)
        collection_store.complete()

def copy_collection_from(src_collection_uuid, dst_collection_uuid, provider_uuid):
    src_collection = get_collection_by_uuid(src_collection_uuid)

    if src_collection.provider_uuid != provider_uuid and not src_collection.is_public:
        raise PermissionError()

    if dst_collection_uuid is None:
        dst_collection = {
            "provider_uuid": provider_uuid,
            "name": src_collection.name,
            "is_public": False
        }

        dst_collection_uuid = create_collection(Collection(**dst_collection))
    
    copy_items_by_collection_uuid(src_collection_uuid, dst_collection_uuid, provider_uuid)
    return dst_collection_uuid
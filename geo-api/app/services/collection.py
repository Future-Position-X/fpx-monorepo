from app.stores.collection import CollectionStore


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
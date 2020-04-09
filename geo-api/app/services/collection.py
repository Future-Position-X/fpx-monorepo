from app.stores.collection import CollectionStore


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

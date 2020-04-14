from app.stores.item import ItemStore
from app.models.item import Item

from app.services.collection import get_collection_uuid_by_collection_name


def get_items_by_collection_uuid(collection_uuid):
    with ItemStore() as item_store:
        items = item_store.find_by_collection_uuid(collection_uuid)
        item_store.complete()
        return items


def get_items_by_collection_name(collection_name):
    collection_uuid = get_collection_uuid_by_collection_name(collection_name)
    with ItemStore() as item_store:
        items = item_store.find_by_collection_uuid(collection_uuid)
        item_store.complete()
        return items


def create_item(item):
    with ItemStore() as item_store:
        uuid = item_store.insert_one(item)
        item_store.complete()
        return uuid


# Maybe this should be in it's own service that handles different formats
def create_items_from_geojson(geojson=None, collection_uuid=None, provider_uuid=None):
    items = [
        Item(**{
            'provider_uuid': provider_uuid,
            'collection_uuid': collection_uuid,
            'geometry': feature['geometry'],
            'properties': feature['properties']
        }) for feature in geojson['features']]

    with ItemStore() as item_store:
        uuids = item_store.insert(items)
        print(uuids)
        item_store.complete()

    return uuids

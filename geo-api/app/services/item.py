from app.stores.item import ItemStore
from app.models.item import Item
from lib.visualizer.renderer import render_feature_collection, render_feature

from app.services.collection import get_collection_uuid_by_collection_name


def get_item_by_uuid_as_geojson(item_uuid):
    with ItemStore() as item_store:
        item = item_store.find_by_uuid_as_geojson(
            item_uuid)
        item_store.complete()
        return item


def get_item_by_uuid_as_png(item_uuid, width, height, map_id):
    with ItemStore() as item_store:
        item = item_store.find_by_uuid_as_geojson(item_uuid)
        item_store.complete()

    return render_feature(item, width, height, map_id)


def get_items_by_collection_uuid(collection_uuid, filters):
    with ItemStore() as item_store:
        items = item_store.find_by_collection_uuid(collection_uuid, filters)
        item_store.complete()
        return items


def get_items_by_collection_uuid_as_geojson(collection_uuid, filters):
    with ItemStore() as item_store:
        items = item_store.find_by_collection_uuid_as_geojson(collection_uuid, filters)
        item_store.complete()
        return items


def get_items_by_collection_uuid_as_png(collection_uuid, filters, width, height, map_id):
    with ItemStore() as item_store:
        items = item_store.find_by_collection_uuid_as_geojson(collection_uuid, filters)
        item_store.complete()

    return render_feature_collection(items, width, height, map_id)


def get_items_within_radius_as_geojson(point_radius, filters):
    with ItemStore() as item_store:
        items = item_store.find_within_radius_as_geojson(
            filters, **point_radius)
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


def delete_item(item_uuid):
    with ItemStore() as item_store:
        item_store.delete(item_uuid)
        item_store.complete()


def update_item(item_uuid, item):
    with ItemStore() as item_store:
        item_store.update(item_uuid, item)
        item_store.complete()


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
        item_store.remove_items_by_provider_uuid(provider_uuid)
        uuids = item_store.insert(items)
        item_store.complete()

    return uuids


def add_items_from_geojson(geojson=None, collection_uuid=None, provider_uuid=None):
    items = [
        Item(**{
            'provider_uuid': provider_uuid,
            'collection_uuid': collection_uuid,
            'geometry': feature['geometry'],
            'properties': feature['properties']
        }) for feature in geojson['features']]

    with ItemStore() as item_store:
        uuids = item_store.insert(items)
        item_store.complete()

    return uuids


def delete_items_by_collection_uuid(collection_uuid):
    with ItemStore() as item_store:
        item_store.delete_items(collection_uuid)
        item_store.complete()
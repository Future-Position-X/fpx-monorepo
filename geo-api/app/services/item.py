from app.stores.item import ItemStore
from app.dto import ItemDTO
from lib.visualizer.renderer import render_feature_collection, render_feature

from app.models import Item as ItemDB

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

def get_items_by_collection_name(collection_name, current_provider_uuid, filters):
    with ItemStore() as item_store:
        items = item_store.find_by_collection_name(collection_name, current_provider_uuid, filters)
        item_store.complete()
        return items

def get_items_by_collection_uuid_as_geojson(collection_uuid, filters, transforms):
    with ItemStore() as item_store:
        items = item_store.find_by_collection_uuid_as_geojson(collection_uuid, filters, transforms)
        item_store.complete()
        return items


def get_items_by_collection_uuid_as_png(collection_uuid, filters, width, height, map_id, transforms):
    with ItemStore() as item_store:
        items = item_store.find_by_collection_uuid_as_geojson(collection_uuid, filters, transforms)
        item_store.complete()

    return render_feature_collection(items, width, height, map_id)


def get_items_by_collection_name_as_png(collection_name, current_provider_uuid, filters, width, height, map_id):
    with ItemStore() as item_store:
        items = item_store.find_by_collection_name_as_geojson(collection_name, current_provider_uuid, filters)
        item_store.complete()

    return render_feature_collection(items, width, height, map_id)


def get_items_by_collection_name_as_geojson(collection_name, current_provider_uuid, filters):
    with ItemStore() as item_store:
        geojson = item_store.find_by_collection_name_as_geojson(collection_name, current_provider_uuid, filters)
        item_store.complete()
        return geojson

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
        ItemDTO(**{
            'provider_uuid': provider_uuid,
            'collection_uuid': collection_uuid,
            'geometry': feature['geometry'],
            'properties': feature['properties']
        }) for feature in geojson['features']]

    with ItemStore() as item_store:
        item_store.remove_items_by_collection_uuid(provider_uuid, collection_uuid)
        uuids = item_store.insert(items)
        item_store.complete()

    return uuids


def add_items_from_geojson(geojson=None, collection_uuid=None, provider_uuid=None):
    items = [
        ItemDTO(**{
            'provider_uuid': provider_uuid,
            'collection_uuid': collection_uuid,
            'geometry': feature['geometry'],
            'properties': feature['properties']
        }) for feature in geojson['features']]

    with ItemStore() as item_store:
        uuids = item_store.insert(items)
        item_store.complete()

    return uuids


def update_items_from_geojson(feature_collection):
    with ItemStore() as item_store:
        for f in feature_collection['features']:
            item_store.update(f['id'],
                              ItemDTO(**{
                    'geometry': f['geometry'],
                    'properties': f['properties']
                }))

        item_store.complete()


def delete_items_by_collection_uuid(collection_uuid):
    with ItemStore() as item_store:
        item_store.delete_items(collection_uuid)
        item_store.complete()


def copy_items_by_collection_uuid(src_collection_uuid, dest_collection_uuid):
    ItemDB.copy_items(src_collection_uuid, dest_collection_uuid)
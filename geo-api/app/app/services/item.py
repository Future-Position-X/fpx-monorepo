from typing import List
from uuid import UUID, uuid4

from app.dto import InternalUserDTO, ItemDTO
from app.models import Collection, Item
from app.models.base_model import to_model, to_models


def get_items(user: InternalUserDTO, filters: dict, transforms: dict) -> List[ItemDTO]:
    items = Item.find_readable(user, filters, transforms)
    return items


def get_collection_items(
    user: InternalUserDTO, collection_uuid: UUID, filters: dict, transforms: dict
) -> List[ItemDTO]:
    items = Item.find_readable_by_collection_uuid(
        user, collection_uuid, filters, transforms
    )
    return items


def get_collection_items_by_name(
    user: InternalUserDTO, collection_name: str, filters: dict, transforms: dict
) -> List[ItemDTO]:
    items = Item.find_readable_by_collection_name(
        user, collection_name, filters, transforms
    )
    return items


def create_collection_item(
    user: InternalUserDTO, collection_uuid: UUID, item_dto: ItemDTO
) -> ItemDTO:
    coll = Collection.find_writeable_or_fail(user, collection_uuid)
    item_dto.collection_uuid = coll.uuid  # type: ignore
    item = Item(**item_dto.to_dict())
    item.save()
    item.session.commit()
    return to_model(item, ItemDTO)


def replace_collection_items(
    user: InternalUserDTO, collection_uuid: UUID, items: List[ItemDTO]
) -> List[ItemDTO]:
    return create_collection_items(user, collection_uuid, items, replace=True)


def add_collection_items(
    user: InternalUserDTO, collection_uuid: UUID, items: List[ItemDTO]
) -> List[ItemDTO]:
    return create_collection_items(user, collection_uuid, items, replace=False)


def create_collection_items(
    user: InternalUserDTO,
    collection_uuid: UUID,
    items: List[ItemDTO],
    replace: bool = False,
) -> List[ItemDTO]:
    collection = Collection.find_writeable_or_fail(user, collection_uuid)

    if replace:
        Item.where(collection_uuid=collection.uuid).delete()
    new_items: List[Item] = [
        Item(**{**item.to_dict(), **{"uuid": uuid4()}}) for item in items
    ]
    Item.session.bulk_save_objects(new_items)
    Item.session.commit()
    uuids = []
    for item in new_items:
        if isinstance(item.uuid, str):
            uuids.append(UUID(item.uuid))
        else:
            uuids.append(item.uuid)
    fetched_items = Item.find_writeable(user, uuids)
    return to_models(fetched_items, ItemDTO)


def delete_collection_items(user: InternalUserDTO, collection_uuid: UUID) -> None:
    Item.delete_by_collection_uuid(user, collection_uuid)


def get_collection_item(
    user: InternalUserDTO, collection_uuid: UUID, item_uuid: UUID
) -> ItemDTO:
    item = Item.find_readable_or_fail(user, item_uuid, collection_uuid)
    return to_model(item, ItemDTO)


def get_item(user: InternalUserDTO, item_uuid: UUID) -> ItemDTO:
    item = Item.find_readable_or_fail(user, item_uuid)
    return to_model(item, ItemDTO)


def delete_collection_item(
    user: InternalUserDTO, collection_uuid: UUID, item_uuid: UUID
) -> None:
    Item.delete_writeable(user, item_uuid, collection_uuid)


def delete_item(user: InternalUserDTO, item_uuid: UUID) -> None:
    Item.delete_writeable(user, item_uuid)


def update_items(user: InternalUserDTO, items_update: List[ItemDTO]) -> List[ItemDTO]:
    items = Item.find_writeable(user, [item.uuid for item in items_update])

    for item in items:
        item_new = [
            item_new
            for item_new in items_update
            if str(item_new.uuid) == str(item.uuid)
        ][0]
        item.properties = item_new.properties
        item.geometry = item_new.geometry
        item.save()

    Item.session.commit()
    return to_models(items, ItemDTO)


def update_collection_items(
    user: InternalUserDTO, collection_uuid: UUID, items_update: List[ItemDTO]
) -> List[ItemDTO]:
    items = Item.find_writeable_by_collection_uuid(
        user, collection_uuid, [item.uuid for item in items_update]
    )

    for item in items:
        item_new = [
            item_new
            for item_new in items_update
            if str(item_new.uuid) == str(item.uuid)
        ][0]
        item.properties = item_new.properties
        item.geometry = item_new.geometry
        item.save()

    Item.session.commit()
    return to_models(items, ItemDTO)


def update_item(
    user: InternalUserDTO, item_uuid: UUID, item_update: ItemDTO
) -> ItemDTO:
    item = Item.find_writeable_or_fail(user, item_uuid)

    item.properties = item_update.properties
    item.geometry = item_update.geometry

    item.save()
    item.session.commit()
    return to_model(item, ItemDTO)


def update_collection_item(
    user: InternalUserDTO, collection_uuid: UUID, item_uuid: UUID, item_update: ItemDTO
) -> ItemDTO:
    item = Item.find_writeable_or_fail(user, item_uuid, collection_uuid)

    item.properties = item_update.properties
    item.geometry = item_update.geometry

    item.save()
    item.session.commit()
    return to_model(item, ItemDTO)


def copy_items_by_collection_uuid(
    src_collection_uuid: UUID, dest_collection_uuid: UUID
) -> None:
    Item.copy_items(src_collection_uuid, dest_collection_uuid)

from typing import List, Optional
from uuid import UUID

from sqlalchemy_mixins import ModelNotFoundError

from app.dto import CollectionDTO, InternalUserDTO
from app.models import Collection
from app.models.base_model import to_model, to_models
from app.services.item import copy_items_by_collection_uuid


def get_all_accessable_collections(user: InternalUserDTO) -> List[CollectionDTO]:
    collections = Collection.find_readable(user)
    return to_models(collections, CollectionDTO)


def create_collection(
    user: InternalUserDTO, collection: CollectionDTO
) -> CollectionDTO:
    collection.provider_uuid = user.provider_uuid
    collection = Collection(**collection.to_dict())
    collection.save()
    collection.session.commit()
    return to_model(collection, CollectionDTO)


def get_collection_by_uuid(
    user: InternalUserDTO, collection_uuid: UUID
) -> CollectionDTO:
    collection = Collection.find_readable_or_fail(user, collection_uuid)
    return to_model(collection, CollectionDTO)


def delete_collection_by_uuid(user: InternalUserDTO, collection_uuid: UUID) -> None:
    collection = Collection.find_writeable_or_fail(user, collection_uuid)
    collection.delete()
    collection.session.commit()


def update_collection_by_uuid(
    user: InternalUserDTO, collection_uuid: UUID, collection_update: CollectionDTO
) -> CollectionDTO:
    collection = Collection.find_writeable_or_fail(user, collection_uuid)
    collection.name = collection_update.name
    collection.is_public = collection_update.is_public
    collection.save()
    collection.session.commit()
    return to_model(collection, CollectionDTO)


def copy_collection_from(
    user: InternalUserDTO,
    src_collection_uuid: UUID,
    dst_collection_uuid: Optional[UUID],
) -> CollectionDTO:
    try:
        src_collection = Collection.find_readable_or_fail(user, src_collection_uuid)
    except ModelNotFoundError:
        raise PermissionError()

    if dst_collection_uuid is None:
        dst_collection_dict = {
            "provider_uuid": user.provider_uuid,
            "name": f"{src_collection.name}_copy",
            "is_public": False,
        }

        dst_collection = Collection.create(**dst_collection_dict)
        dst_collection_uuid = dst_collection.uuid

    copy_items_by_collection_uuid(src_collection_uuid, dst_collection_uuid)
    src_collection.session.commit()
    collection = Collection.find_readable_or_fail(user, dst_collection_uuid)
    return to_model(collection, CollectionDTO)

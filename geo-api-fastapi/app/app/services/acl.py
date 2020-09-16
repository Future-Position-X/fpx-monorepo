from typing import List
from uuid import UUID

from app.dto import InternalUserDTO, ACLDTO
from app.models import ACL, Collection, Item, Provider, User
from app.models.base_model import to_models, to_model

def get_all_readable_acls(user: InternalUserDTO) -> List[ACLDTO]:
    acls = ACL.find_accessable(user)
    return to_models(acls, ACLDTO)


def get_acl_by_uuid(user: InternalUserDTO, acl_uuid: UUID) -> ACLDTO:
    acl = ACL.find_accessable_or_fail(user, acl_uuid)
    return to_model(acl, ACLDTO)


def create_acl(user: InternalUserDTO, acl: ACLDTO) -> ACLDTO:
    if acl.collection_uuid:
        collection = Collection.find_writeable_or_fail(user, acl.collection_uuid)
        if collection.provider_uuid != user.provider_uuid:
            raise PermissionError

    if acl.item_uuid:
        item = Item.find_writeable_or_fail(user, acl.item_uuid)
        if item.collection.provider_uuid != user.provider_uuid:
            raise PermissionError

    if acl.granted_provider_uuid:
        Provider.find_or_fail(acl.granted_provider_uuid)

    if acl.granted_user_uuid:
        User.find_or_fail(acl.granted_user_uuid)

    acl.provider_uuid = user.provider_uuid
    acl = ACL(**acl.to_dict())
    acl.save()
    acl.session.commit()
    return to_model(acl, ACLDTO)


def delete_acl_by_uuid(user: InternalUserDTO, acl_uuid: UUID) -> None:
    acl = ACL.find_accessable_or_fail(user, acl_uuid)
    acl.delete()
    acl.session.commit()

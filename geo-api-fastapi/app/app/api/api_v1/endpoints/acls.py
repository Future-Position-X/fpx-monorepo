from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import schemas, models, services
from app.api import deps

router = APIRouter()


@router.get("/acls")
def get_acls(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user),
) -> List[schemas.ACL]:
    acls = services.acl.get_all_readable_acls(current_user)
    return [schemas.ACL.from_dto(acl) for acl in acls]


@router.post("/acls", status_code=201)
def create_acl(
    acl_in: schemas.ACLCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),

) -> schemas.ACL:
    if not (
            bool(acl_in.granted_provider_uuid) != bool(acl_in.granted_user_uuid)
            and bool(acl_in.collection_uuid) != bool(acl_in.item_uuid)
            and acl_in.access in ["read", "write"]
    ):
        raise ValueError

    acl = schemas.ACL.from_dto(services.acl.create_acl(current_user, acl_in.to_dto()))
    return acl


@router.get("/acls/{acl_uuid}")
def get_acl(
        acl_uuid: UUID,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user),
) -> List[schemas.ACL]:
    acl = services.acl.get_acl_by_uuid(current_user, acl_uuid)
    return schemas.ACL.from_dto(acl)


@router.delete("/acls/{acl_uuid}", status_code=204)
def delete_acl(
        acl_uuid: UUID,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user),
) -> None:
    services.acl.delete_acl_by_uuid(current_user, acl_uuid)
    return None

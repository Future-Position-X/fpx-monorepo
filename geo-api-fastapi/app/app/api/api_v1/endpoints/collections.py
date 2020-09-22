from typing import List, Optional
from uuid import UUID

from app import schemas, models, services
from app.api import deps
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/collections")
def get_collections(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user_or_guest),
) -> List[schemas.Collection]:
    collections = services.collection.get_all_accessable_collections(current_user)
    return [schemas.Collection.from_dto(collection) for collection in collections]


@router.post("/collections", status_code=201)
def create_collection(
    collection_in: schemas.CollectionCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> schemas.Collection:
    collection = schemas.Collection.from_dto(services.collection.create_collection(current_user, collection_in.to_dto()))
    return collection


@router.get("/collections/{collection_uuid}")
def get_collection(
        collection_uuid: UUID,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user_or_guest),
) -> schemas.Collection:
    collection = services.collection.get_collection_by_uuid(current_user, collection_uuid)
    return schemas.Collection.from_dto(collection)


@router.put("/collections/{collection_uuid}", status_code=204)
def update_collection(
        collection_uuid: UUID,
        collection_in: schemas.CollectionUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user),
) -> None:
    services.collection.update_collection_by_uuid(current_user, collection_uuid, collection_in.to_dto())
    return None


@router.delete("/collections/{collection_uuid}", status_code=204)
def delete_collection(
        collection_uuid: UUID,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user),
) -> None:
    services.collection.delete_collection_by_uuid(current_user, collection_uuid)
    return None


@router.post("/collections/{src_collection_uuid}/copy", status_code=201)
@router.post("/collections/{src_collection_uuid}/copy/{dst_collection_uuid}", status_code=201)
def create_collection(
    src_collection_uuid: UUID,
    dst_collection_uuid: Optional[UUID],
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> schemas.Collection:
    collection = schemas.Collection.from_dto(services.collection.copy_collection_from(current_user, src_collection_uuid, dst_collection_uuid))
    return collection

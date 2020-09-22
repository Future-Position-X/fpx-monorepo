from typing import List
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
) -> List[schemas.ACL]:
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
) -> List[schemas.ACL]:
    collection = services.collection.get_collection_by_uuid(current_user, collection_uuid)
    return schemas.Collection.from_dto(collection)


@router.delete("/collections/{collection_uuid}", status_code=204)
def delete_collection(
        collection_uuid: UUID,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user),
) -> None:
    services.collection.delete_collection_by_uuid(current_user, collection_uuid)
    return None


@router.put("/collections/{collection_uuid}", status_code=204)
def update_collection(
        collection_uuid: UUID,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user),
) -> None:
    services.collection.delete_collection_by_uuid(current_user, collection_uuid)
    return None

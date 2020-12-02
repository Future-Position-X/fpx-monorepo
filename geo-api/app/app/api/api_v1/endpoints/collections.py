from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile
from geojson_pydantic.features import Feature

from app import models, schemas, services
from app.api import deps
from app.api.api_v1.endpoints.items import map_features_to_item_dtos
from app.dto import CollectionDTO

router = APIRouter()


@router.get("/collections")
def get_collections(
    current_user: models.User = Depends(deps.get_current_user_or_guest),
) -> List[schemas.Collection]:
    collections = services.collection.get_all_accessable_collections(current_user)
    return [schemas.Collection.from_dto(collection) for collection in collections]


@router.post("/collections", status_code=201)
def create_collection(
    collection_in: schemas.CollectionCreate,
    current_user: models.User = Depends(deps.get_current_user),
) -> schemas.Collection:
    collection = schemas.Collection.from_dto(
        services.collection.create_collection(current_user, collection_in.to_dto())
    )
    return collection


@router.post("/collections/from_file", status_code=201)
async def create_upload_file(
    collection_name: str = Form(...),
    is_public: bool = Form(...),
    file: UploadFile = File(...),
    current_user: models.User = Depends(deps.get_current_user),
) -> schemas.Collection:
    print("collection_name", collection_name)
    print("is_public", is_public)
    print("file name:", file.filename)
    print("mime:", file.content_type)
    collection = schemas.Collection.from_dto(
        services.collection.create_collection(
            current_user,
            CollectionDTO(**{"name": collection_name, "is_public": is_public}),
        )
    )

    geojson = services.shapefile.convert_zip_to_feature_collection(file)

    item_dtos = map_features_to_item_dtos([Feature(**f) for f in geojson["features"]])

    for item in item_dtos:
        item.collection_uuid = collection.uuid

    services.item.add_collection_items(current_user, collection.uuid, item_dtos)
    return collection


@router.get("/collections/{collection_uuid}")
def get_collection(
    collection_uuid: UUID,
    current_user: models.User = Depends(deps.get_current_user_or_guest),
) -> schemas.Collection:
    collection = services.collection.get_collection_by_uuid(
        current_user, collection_uuid
    )
    return schemas.Collection.from_dto(collection)


@router.put("/collections/{collection_uuid}", status_code=204)
def update_collection(
    collection_uuid: UUID,
    collection_in: schemas.CollectionUpdate,
    current_user: models.User = Depends(deps.get_current_user),
) -> None:
    services.collection.update_collection_by_uuid(
        current_user, collection_uuid, collection_in.to_dto()
    )
    return None


@router.delete("/collections/{collection_uuid}", status_code=204)
def delete_collection(
    collection_uuid: UUID, current_user: models.User = Depends(deps.get_current_user)
) -> None:
    services.collection.delete_collection_by_uuid(current_user, collection_uuid)
    return None


@router.post("/collections/{src_collection_uuid}/copy", status_code=201)
def copy_to_new_collection(
    src_collection_uuid: UUID,
    collection_in: schemas.CollectionCreate,
    current_user: models.User = Depends(deps.get_current_user),
) -> schemas.Collection:
    collection = schemas.Collection.from_dto(
        services.collection.copy_collection_to_new(
            current_user, src_collection_uuid, collection_in.to_dto()
        )
    )
    return collection


@router.post(
    "/collections/{src_collection_uuid}/copy/{dst_collection_uuid}", status_code=201
)
def copy_to_collection(
    src_collection_uuid: UUID,
    dst_collection_uuid: UUID,
    current_user: models.User = Depends(deps.get_current_user),
) -> schemas.Collection:
    collection = schemas.Collection.from_dto(
        services.collection.copy_collection_from(
            current_user, src_collection_uuid, dst_collection_uuid
        )
    )
    return collection

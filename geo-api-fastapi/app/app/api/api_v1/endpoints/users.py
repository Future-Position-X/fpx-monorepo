from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps

router = APIRouter()

@router.get("/users")
def get_users(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user_or_guest),
) -> List[schemas.User]:
    users = services.user.ge2t_users()
    return [schemas.User.from_dto(user) for user in users]


@router.post("/users", status_code=201)
def create_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user_or_guest),
) -> schemas.User:
    user = schemas.User.from_dto(services.user.create_user(user_in.to_dto()))
    return user


@router.get("/users/uuid")
def get_current_user_uuid(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user),
) -> schemas.User:
    user = services.user.get_user(current_user.uuid)
    return schemas.User.from_dto(user)


@router.get("/users/{user_uuid}")
def get_user(
        user_uuid: UUID,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user_or_guest),
) -> schemas.User:
    user = services.user.get_user(user_uuid)
    return schemas.User.from_dto(user)


@router.put("/users/{user_uuid}", status_code=204)
def update_user(
        user_uuid: UUID,
        user_in: schemas.UserUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user),
) -> None:
    services.user.update_user(current_user.provider_uuid, user_uuid, user_in.to_dto())
    return None


@router.delete("/users/{user_uuid}", status_code=204)
def delete_user(
        user_uuid: UUID,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user),
) -> None:
    services.user.delete_user(current_user.provider_uuid, user_uuid)
    return None

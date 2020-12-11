# from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends

from app import schemas, services
from app.api import deps
from app.utils import send_new_account_email

router = APIRouter()


# @router.get("/users")
# def get_users() -> List[schemas.User]:
#     users = services.user.get_users()
#     return [schemas.User.from_dto(user) for user in users]


@router.post("/users", status_code=201)
def create_user(user_in: schemas.UserCreate,) -> schemas.User:
    user = schemas.User.from_dto(services.user.create_user(user_in.to_dto()))
    send_new_account_email(email_to=user.email, username=user.email, password="nopassword")
    return user


@router.get("/users/uuid")
def get_current_user_uuid(
    current_user: schemas.User = Depends(deps.get_current_user),
) -> schemas.User:
    user = services.user.get_user(current_user.uuid)
    return schemas.User.from_dto(user)


@router.get("/users/{user_uuid}")
def get_user(
    user_uuid: UUID, current_user: schemas.User = Depends(deps.get_current_user)
) -> schemas.User:
    if user_uuid != current_user.uuid:
        raise PermissionError

    user = services.user.get_user(current_user.uuid)
    return schemas.User.from_dto(user)


@router.put("/users/{user_uuid}", status_code=204)
def update_user(
    user_uuid: UUID,
    user_in: schemas.UserUpdate,
    current_user: schemas.User = Depends(deps.get_current_user),
) -> None:
    if user_uuid != current_user.uuid:
        raise PermissionError

    services.user.update_user(current_user.provider_uuid, user_uuid, user_in.to_dto())
    return None


@router.delete("/users/{user_uuid}", status_code=204)
def delete_user(
    user_uuid: UUID, current_user: schemas.User = Depends(deps.get_current_user)
) -> None:
    if user_uuid != current_user.uuid:
        raise PermissionError

    services.user.delete_user(current_user.provider_uuid, user_uuid)
    return None

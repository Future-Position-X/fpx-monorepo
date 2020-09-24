from typing import List, Optional
from uuid import UUID

import bcrypt
from sqlalchemy.exc import IntegrityError

from app.core.security import verify_password
from app.dto import ProviderDTO, UserDTO
from app.errors import UnauthorizedError
from app.models import User
from app.services.provider import create_provider
from app.models.base_model import to_models, to_model


def get_users() -> List[UserDTO]:
    return to_models(User.all(), UserDTO)


def create_user(user: UserDTO) -> UserDTO:
    user.password = bcrypt.hashpw(
        user.password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")
    User.session.begin_nested()
    try:
        provider = create_provider(ProviderDTO(name=user.email))
        user.provider_uuid = provider.uuid
        user = User.create(**user.to_dict())
    except IntegrityError:
        User.session.rollback()
        raise ValueError
    user.session.commit()
    return to_model(user, UserDTO)


def get_user(user_uuid: UUID) -> UserDTO:
    return to_model(User.find_or_fail(user_uuid), UserDTO)


def get_user_by_email(email: str) -> UserDTO:
    return to_model(User.find_or_fail(email=email), UserDTO)


def update_user(provider_uuid: UUID, user_uuid: UUID, user_update: UserDTO) -> UserDTO:
    user = User.first_or_fail(provider_uuid=provider_uuid, uuid=user_uuid)
    user.password = bcrypt.hashpw(
        user_update.password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")
    user.save()
    user.session.commit()
    return to_model(user, UserDTO)


def delete_user(provider_uuid: UUID, user_uuid: UUID) -> None:
    user = User.first_or_fail(provider_uuid=provider_uuid, uuid=user_uuid)
    user.delete()
    user.session.commit()


def authenticate(email: str, password: str) -> Optional[UserDTO]:
    user = User.first(email=email)
    if not user or not verify_password(password, user.password):
        raise UnauthorizedError
    return to_model(user, UserDTO)

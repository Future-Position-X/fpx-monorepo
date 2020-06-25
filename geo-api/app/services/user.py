from typing import List
from uuid import UUID

import bcrypt
from sqlalchemy.dialects.postgresql import psycopg2
from sqlalchemy.exc import IntegrityError

from app.dto import ProviderDTO, UserDTO
from app.models import User, to_models, to_model
from app.services.provider import create_provider


def get_users() -> List[UserDTO]:
    return to_models(User.all(), UserDTO)


def create_user(user: UserDTO) -> UserDTO:
    user.password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    User.session.begin_nested()
    provider = create_provider(ProviderDTO(name=user.email))
    user.provider_uuid = provider.uuid
    try:
        user = User.create(**user.to_dict())
    except IntegrityError as e:
        User.session.rollback()
        raise ValueError
    user.session.commit()
    return to_model(user, UserDTO)


def get_user(user_uuid: UUID) -> UserDTO:
    return to_model(User.find_or_fail(user_uuid), UserDTO)


def update_user(provider_uuid: UUID, user_uuid: UUID, user_update: UserDTO) -> UserDTO:
    user = User.first_or_fail(provider_uuid=provider_uuid, uuid=user_uuid)
    user.password = bcrypt.hashpw(user_update.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    user.save()
    user.session.commit()
    return to_model(user, UserDTO)


def delete_user(provider_uuid: UUID, user_uuid: UUID) -> None:
    user = User.first_or_fail(provider_uuid=provider_uuid, uuid=user_uuid)
    user.delete()
    user.session.commit()

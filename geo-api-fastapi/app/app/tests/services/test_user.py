import pytest
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import crud, services
from app.core.security import verify_password
from app.errors import UnauthorizedError
from app.schemas.user import UserCreate, UserUpdate
from app.tests.utils.utils import random_email, random_lower_string


def test_create_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = services.user.create_user(user_in.to_dto())
    assert user.email == email
    assert hasattr(user, "password")


def test_authenticate_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = services.user.create_user(user_in.to_dto())
    authenticated_user = services.user.authenticate(email=email, password=password)
    assert authenticated_user
    assert user.email == authenticated_user.email


def test_not_authenticate_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    with pytest.raises(UnauthorizedError):
        user = services.user.authenticate(email=email, password=password)
        assert user is None


def test_get_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = services.user.create_user(user_in.to_dto())
    user_2 = services.user.get_user(user.uuid)
    assert user_2
    assert user.email == user_2.email
    assert jsonable_encoder(user) == jsonable_encoder(user_2)


def test_update_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = services.user.create_user(user_in.to_dto())
    new_password = random_lower_string()
    user_in_update = UserUpdate(password=new_password)
    services.user.update_user(user.provider_uuid, user.uuid, user_in_update.to_dto())
    user_2 = services.user.get_user(user.uuid)
    assert user_2
    assert user.email == user_2.email
    assert verify_password(new_password, user_2.password)

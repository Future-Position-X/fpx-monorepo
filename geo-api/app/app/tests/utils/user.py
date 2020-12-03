from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import services
from app.core.config import settings
from app.schemas.user import User, UserCreate, UserUpdate
from app.tests.utils.utils import random_email, random_lower_string


def user_authentication_headers(
    *, client: TestClient, email: str, password: str
) -> Dict[str, str]:
    data = {"username": email, "password": password}

    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


def create_random_user(db: Session) -> User:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = services.user.create_user(user_in.to_dto())
    return User.from_dto(user)


def authentication_token_from_email(
    *, client: TestClient, email: str, db: Session
) -> Dict[str, str]:
    """
    Return a valid token for the user with given email.

    If the user doesn't exist it is created first.
    """
    password = random_lower_string()
    user = services.user.get_user_by_email(email)
    if not user:
        user_in_create = UserCreate(email=email, password=password)
        user = services.user.create_user(user_in_create.to_dto())
    else:
        user_in_update = UserUpdate(password=password)
        user = services.user.update_user(
            user.provider_uuid, user.uuid, user_in_update.to_dto()
        )

    return user_authentication_headers(client=client, email=email, password=password)

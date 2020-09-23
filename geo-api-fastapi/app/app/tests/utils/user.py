import random
from typing import Dict

from fastapi.testclient import TestClient
from shapely.geometry import Point
from sqlalchemy.orm import Session

from app import crud, services
from app.core.config import settings
from app.dto import InternalUserDTO
from app.schemas import CollectionCreate, Collection, ItemCreate, Item
from app.schemas.user import UserCreate, UserUpdate, User
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


def create_random_collection(user: User) -> Collection:
    name = random_lower_string()
    collection_in = CollectionCreate(name=name, is_public=False)
    collection = services.collection.create_collection(InternalUserDTO(**user.dict()), collection_in.to_dto())
    return Collection.from_dto(collection)

def create_random_item(user: User, collection: Collection) -> Item:
    geometry = Point(random.random(), random.random())
    properties = {"name": random_lower_string()}
    item_in = ItemCreate(geometry=geometry, properties=properties)
    item = services.item.create_collection_item(InternalUserDTO(**user.dict()), collection.uuid, item_in.to_dto())
    return Item.from_dto(item)

def authentication_token_from_email(
    *, client: TestClient, email: str, db: Session
) -> Dict[str, str]:
    """
    Return a valid token for the user with given email.

    If the user doesn't exist it is created first.
    """
    password = random_lower_string()
    user = crud.user.get_by_email(db, email=email)
    if not user:
        user_in_create = UserCreate(username=email, email=email, password=password)
        user = crud.user.create(db, obj_in=user_in_create)
    else:
        user_in_update = UserUpdate(password=password)
        user = crud.user.update(db, db_obj=user, obj_in=user_in_update)

    return user_authentication_headers(client=client, email=email, password=password)

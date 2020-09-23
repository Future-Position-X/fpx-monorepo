import pytest
from geoalchemy2.shape import to_shape
from shapely.geometry import Point
from sqlalchemy.orm import Session
from sqlalchemy_mixins import ModelNotFoundError

from app import services
from app.dto import InternalUserDTO
from app.schemas.item import ItemCreate, ItemUpdate, Item
from app.tests.utils.user import create_random_user, create_random_collection, create_random_item
from app.tests.utils.utils import random_lower_string


def test_create_item(db: Session) -> None:
    geometry = Point(0.0, 0.0)
    properties = {"name": "test-name1"}
    item_in = ItemCreate(geometry=geometry, properties=properties)
    user = create_random_user(db)
    collection = create_random_collection(user)
    item = services.item.create_collection_item(InternalUserDTO(**user.dict()), collection.uuid, item_in.to_dto())
    assert to_shape(item.geometry) == geometry
    assert item.properties == properties
    assert item.collection_uuid == collection.uuid


def test_get_item(db: Session) -> None:
    user = create_random_user(db)
    collection = create_random_collection(user)
    item = create_random_item(user, collection)

    stored_item = Item.from_dto(services.item.get_item(InternalUserDTO(**user.dict()), item.uuid))
    assert stored_item
    assert item.uuid == stored_item.uuid
    assert item.geometry == stored_item.geometry
    assert item.properties == stored_item.properties
    assert item.collection_uuid == stored_item.collection_uuid


def test_update_item(db: Session) -> None:
    user = create_random_user(db)
    collection = create_random_collection(user)
    item = create_random_item(user, collection)
    properties = {"name": random_lower_string()}
    item_update = ItemUpdate(uuid=item.uuid, geometry=item.geometry, properties=properties)
    item2 = Item.from_dto(services.item.update_item(InternalUserDTO(**user.dict()), item.uuid, item_update.to_dto()))
    stored_item = Item.from_dto(services.item.get_item(InternalUserDTO(**user.dict()), item.uuid))
    assert item.uuid == item2.uuid == stored_item.uuid
    assert item.geometry == item2.geometry == stored_item.geometry
    assert item2.properties == properties == stored_item.properties
    assert item.collection_uuid == item2.collection_uuid == stored_item.collection_uuid


def test_delete_item(db: Session) -> None:
    user = create_random_user(db)
    collection = create_random_collection(user)
    item = create_random_item(user, collection)
    services.item.delete_item(InternalUserDTO(**user.dict()), item.uuid)
    with pytest.raises(ModelNotFoundError):
        services.item.get_item(InternalUserDTO(**user.dict()), item.uuid)

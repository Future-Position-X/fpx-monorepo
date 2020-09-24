import random

from shapely.geometry import Point

from app import services
from app.dto import InternalUserDTO
from app.schemas import User, Collection, CollectionCreate
from app.schemas.item import ItemCreate, Item
from app.tests.utils.utils import random_lower_string


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

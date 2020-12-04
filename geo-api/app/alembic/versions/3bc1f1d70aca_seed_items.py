"""seed items

Revision ID: 3bc1f1d70aca
Revises: 302c23c2932d
Create Date: 2020-06-22 14:15:39.211348

"""
import json
import os

from shapely.geometry import shape
from sqlalchemy.orm.session import Session

from alembic import op
from app.models import Collection, Item, Provider
from app.models.base_model import BaseModel

# revision identifiers, used by Alembic.
revision = "3bc1f1d70aca"
down_revision = "302c23c2932d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    session = Session(bind=op.get_bind())
    BaseModel.set_session(session)
    # ### commands auto generated by Alembic - please adjust! ###
    provider = Provider.all()[0]
    collection = seed_initial_collection(provider.uuid)
    seed_initial_items(collection.uuid)
    # ### end Alembic commands ###


def seed_initial_collection(provider_uuid: str) -> Collection:
    collection = Collection.create(
        provider_uuid=provider_uuid, name="__test", is_public=True
    )

    return collection


def seed_initial_items(collection_uuid: str) -> Item:
    pwd = os.getcwd() + "/data/feature_collection.json"
    print(pwd)
    f = open(pwd)
    geojson = json.loads(f.read())
    f.close()

    for feature in geojson["features"]:
        item = Item.create(
            collection_uuid=collection_uuid,
            geometry=shape(feature["geometry"]).to_wkt(),
            properties=feature["properties"],
        )

    return item


def downgrade() -> None:
    session = Session(bind=op.get_bind())
    BaseModel.set_session(session)
    Item.query.delete()
    Collection.query.delete()
from app import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.postgresql import JSONB
from geoalchemy2 import Geometry
import uuid

class Collection(db.Model):
    __tablename__ = 'collections'

    uuid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    provider_uuid = db.Column(UUID(as_uuid=True))
    name = db.Column(db.Text(), unique=True)
    is_public = db.Column(db.Boolean, default=False)
    revision = db.Column(db.Integer, nullable=False)
    created_at = db.Column('created_at', db.DateTime, default=db.func.now())
    updated_at = db.Column('updated_at', db.DateTime, default=db.func.now(), onupdate=db.func.utc_timestamp())
    __mapper_args__ = {
        "version_id_col": revision
    }

    def __init__(self, provider_uuid, name, is_public):
        self.provider_uuid = provider_uuid
        self.name = name
        self.is_public = is_public

    def __repr__(self):
        return '<Collection uuid={}, name={}, is_public={}>'.format(self.uuid, self.name, self.is_public)

class Item(db.Model):
    __tablename__ = 'items'

    uuid = db.Column(UUID(as_uuid=True), primary_key=True, server_default=db.text("gen_random_uuid()"), unique=True, nullable=False)
    provider_uuid = db.Column(UUID(as_uuid=True))
    collection_uuid = db.Column(UUID(as_uuid=True))
    geometry = db.Column(Geometry(geometry_type='GEOMETRY', srid=4326))
    properties = db.Column(JSONB)
    revision = db.Column(db.Integer, nullable=False)
    created_at = db.Column('created_at', db.DateTime, default=db.func.now())
    updated_at = db.Column('updated_at', db.DateTime, default=db.func.now(), onupdate=db.func.utc_timestamp())
    __mapper_args__ = {
        "version_id_col": revision
    }

    def __init__(self, provider_uuid, collection_uuid, geometry, properties):
        self.provider_uuid = provider_uuid
        self.collection_uuid = collection_uuid
        self.geometry = geometry
        self.properties = properties

    def __repr__(self):
        return '<Item uuid={}, provider_uuid={}, collection_uuid={}, geometry=SNIP, properties={}>'.format(self.uuid, self.provider_uuid, self.collection_uuid, self.properties)
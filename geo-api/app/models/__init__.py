from sqlalchemy.orm import aliased

from app import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.postgresql import JSONB
from geoalchemy2 import Geometry, WKTElement, WKBElement
import uuid
from app.models.item import Item as ItemModel

from sqlalchemy_mixins import ActiveRecordMixin, SmartQueryMixin, ReprMixin, SerializeMixin, \
    ModelNotFoundError


class FPXActiveRecordMixin(ActiveRecordMixin):
    __abstract__ = True

    @classmethod
    def first_or_fail(cls, **kwargs):
        result = cls.where(**kwargs).first()
        if result:
            return result
        else:
            raise ModelNotFoundError("{} with matching '{}' was not found"
                                     .format(cls.__name__, kwargs))


class FPXTimestampsMixin:
    __abstract__ = True

    __datetime_callback__ = db.func.now

    created_at = db.Column(db.DateTime,
                           server_default=db.text('now()'),
                           nullable=False)

    updated_at = db.Column(db.DateTime,
                           server_default=db.text('now()'),
                           nullable=False)


@db.event.listens_for(FPXTimestampsMixin, 'before_update', propagate=True)
def _receive_before_update(mapper, connection, target):
    """Listen for updates and update `updated_at` column."""
    target.updated_at = target.__datetime_callback__()


class BaseModel2(db.Model, FPXActiveRecordMixin, SmartQueryMixin, ReprMixin, SerializeMixin, FPXTimestampsMixin):
    __abstract__ = True

    revision = db.Column(db.Integer, server_default=db.text('1'), nullable=False)

    __mapper_args__ = {
        "version_id_col": revision
    }

    pass


class Provider(BaseModel2):
    __tablename__ = 'providers'

    uuid = db.Column(UUID(as_uuid=True), primary_key=True, server_default=db.text("gen_random_uuid()"), unique=True,
                     nullable=False)
    name = db.Column(db.Text(), unique=True)

    collections = db.relationship('Collection', backref='provider', lazy=True)


class User(BaseModel2):
    __tablename__ = 'users'

    uuid = db.Column(UUID(as_uuid=True), primary_key=True, server_default=db.text("gen_random_uuid()"), unique=True,
                     nullable=False)
    email = db.Column(db.Text(), unique=True)
    password = db.Column(db.Text())

    provider_uuid = db.Column(UUID(as_uuid=True), db.ForeignKey('providers.uuid'), index=True, nullable=False)


class Collection(BaseModel2):
    __tablename__ = 'collections'
    __table_args__ = (
        db.UniqueConstraint('provider_uuid', 'name'),)
    uuid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = db.Column(db.Text())
    is_public = db.Column(db.Boolean, default=False)

    items = db.relationship('Item', backref='collection', lazy=True)

    provider_uuid = db.Column(UUID(as_uuid=True), db.ForeignKey('providers.uuid'), index=True, nullable=False)


def append_property_filter_to_where_clause(where_clause, filter, execute_dict):
    params = filter.split(",")

    for i, p in enumerate(params):
        tokens = p.split("=")
        name = "name_" + str(i)
        value = "value_" + str(i)

        where_clause += " properties->>%(" + \
                        name + ")s = %(" + value + ")s"
        execute_dict[name] = tokens[0]
        execute_dict[value] = tokens[1]

        if i < (len(params) - 1):
            where_clause += " AND"

    return where_clause
from sqlalchemy import func, column
from sqlalchemy.sql import select
class Item(BaseModel2):
    __tablename__ = 'items'

    uuid = db.Column(UUID(as_uuid=True), primary_key=True, server_default=db.text("gen_random_uuid()"), unique=True,
                     nullable=False)
    geometry = db.Column(Geometry(geometry_type='GEOMETRY'))
    properties = db.Column(JSONB)

    collection_uuid = db.Column(UUID(as_uuid=True), db.ForeignKey('collections.uuid'), index=True, nullable=False)
    provider_uuid = db.Column(UUID(as_uuid=True), db.ForeignKey('providers.uuid'), index=True, nullable=False)

    def create_where(filters):
        where = ""
        if filters.get('collection_uuid'):
            if len(where) == 0:
                where = "collection_uuid = :collection_uuid"
            else:
                where = " AND collection_uuid = :collection_uuid"

        if filters.get('collection_name'):
            if len(where) == 0:
                where = "collections.name = :collection_name"
            else:
                where = " AND collections.name = :collection_name"

        if filters["valid"]:
            where += " AND ST_IsValid(geometry)"

        if filters["spatial_filter"] and filters["spatial_filter"]["filter"] == "within-distance":
            where += """
            AND ST_DWithin(
                geometry,
                :distance_point,
                :distance_d,
                False
            )
            """

        if filters["spatial_filter"] and filters["spatial_filter"]["filter"] == "intersect":
            where += """
            AND ST_Intersects(
                geometry,
                ST_MakeEnvelope(:envelope_xmin, :envelope_ymin, :envelope_xmax, :envelope_ymax, 4326)
            )
            """

        if filters["spatial_filter"] and filters["spatial_filter"]["filter"] == "within":
            where += """
            AND ST_Within(
                geometry,
                ST_MakeEnvelope(:envelope_xmin, :envelope_ymin, :envelope_xmax, :envelope_ymax, 4326)
            )
            """

        exec_dict = {
            "collection_uuid": filters.get('collection_uuid'),
            "collection_name": filters.get('collection_name'),
            "offset": filters["offset"],
            "limit": filters["limit"],
        }

        if filters['spatial_filter'] and filters['spatial_filter']['filter'] in ['within', 'intersect']:
            exec_dict.update({
                "envelope_xmin": filters['spatial_filter']['envelope']['xmin'],
                "envelope_ymin": filters['spatial_filter']['envelope']['ymin'],
                "envelope_xmax": filters['spatial_filter']['envelope']['xmax'],
                "envelope_ymax": filters['spatial_filter']['envelope']['ymax'],
            })

        if filters['spatial_filter'] and filters['spatial_filter']['filter'] in ['within-distance']:
            exec_dict.update({
                "distance_point": filters['spatial_filter']['distance']['point'].wkt,
                "distance_d": filters['spatial_filter']['distance']['d'],
            })

        if filters["property_filter"] is not None:
            where += " AND "
            where = append_property_filter_to_where_clause(
                where, filters["property_filter"], exec_dict)

        return where, exec_dict

    @classmethod
    def find_by_collection_name(cls, collection_name, filters):
        filters['collection_name'] = collection_name
        where, exec_dict = cls.create_where(filters)
        result = cls.query.join(Item.collection).filter(db.text(where)).params(exec_dict).limit(filters['limit']).offset(filters['offset']).all()
        return result

    @classmethod
    def find_by_collection_name_with_simplify(cls, collection_name, filters, transforms):
        filters['collection_name'] = collection_name
        where, exec_dict = cls.create_where(filters)
        result = cls.session().query(cls.uuid, func.ST_Simplify(cls.geometry, transforms['simplify'], True).label('geometry'),
                                     cls.properties, cls.collection_uuid, cls.provider_uuid, cls.created_at,
                                     cls.updated_at, cls.revision).join(Item.collection).filter(db.text(where)).params(exec_dict).limit(
            filters['limit']).offset(filters['offset']).all()
        result = [ItemModel(**dict(zip(res.keys(), res))) for res in result]
        return result

    @classmethod
    def find_by_collection_uuid(cls, collection_uuid, filters):
        filters['collection_uuid'] = collection_uuid
        where, exec_dict = cls.create_where(filters)
        result = cls.query.filter(db.text(where)).params(exec_dict).limit(filters['limit']).offset(filters['offset']).all()
        return result

    @classmethod
    def find_by_collection_uuid_with_simplify(cls, collection_uuid, filters, transforms):
        filters['collection_uuid'] = collection_uuid
        where, exec_dict = cls.create_where(filters)
        result = cls.session().query(cls.uuid, func.ST_Simplify(cls.geometry, transforms['simplify'], True).label('geometry'),
                                     cls.properties, cls.collection_uuid, cls.provider_uuid, cls.created_at,
                                     cls.updated_at, cls.revision).filter(db.text(where)).params(exec_dict).limit(
            filters['limit']).offset(filters['offset']).all()
        result = [ItemModel(**dict(zip(res.keys(), res))) for res in result]
        return result

    @classmethod
    def copy_items(cls, src_collection_uuid, dest_collection_uuid, provider_uuid):
        cls.session().execute("""
            INSERT INTO items (provider_uuid, collection_uuid, geometry, properties) 
                SELECT :provider_uuid, :dest_collection_uuid, geometry, properties
                FROM items WHERE collection_uuid = :src_collection_uuid
            """, {
            "provider_uuid": provider_uuid,
            "src_collection_uuid": src_collection_uuid,
            "dest_collection_uuid": dest_collection_uuid
        })

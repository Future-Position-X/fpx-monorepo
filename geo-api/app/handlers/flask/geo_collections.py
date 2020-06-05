import rapidjson
from app import app, api, db
from flask_restx import Resource, fields
from app.models.collection import Collection as CollectionModel
from app.models import Collection as CollectionDB
from app.handlers.flask import (
    get_provider_uuid_from_request,

)
from app.services.collection import (
    get_all_collections,
    create_collection,
    delete_collection_by_uuid,
    update_collection_by_uuid,
    get_collection_by_uuid,
    copy_collection_from
)
from flask_jwt_extended import jwt_required
from flask import request, abort

ns = api.namespace('collections', 'Collection operations')

collection_model = api.model('Collection', {
    'uuid': fields.String(description='uuid'),
    'provider_uuid': fields.String(description='provider_uuid'),
    'name': fields.String(description='name'),
    'is_public': fields.String(description='is_public'),
    'revision': fields.String(description='revision'),
    'created_at': fields.String(description='created_at'),
    'updated_at': fields.String(description='updated_at'),
})

create_collection_model = api.model('CreateCollection', {
    'provider_uuid': fields.String(description='provider_uuid'),
    'name': fields.String(description='name'),
    'is_public': fields.String(description='is_public'),
})

update_collection_model = api.model('UpdateCollection', {
    'provider_uuid': fields.String(description='provider_uuid'),
    'name': fields.String(description='name'),
    'is_public': fields.String(description='is_public'),
})

@ns.route('/')
class CollectionList(Resource):
    @jwt_required
    @ns.doc('list_collections')
    @ns.marshal_list_with(collection_model)
    def get(self):
        collections = db.session.query(CollectionDB).all()
        return collections

    @jwt_required
    @ns.doc('create_collection')
    @ns.expect(create_collection_model)
    @ns.marshal_with(collection_model, 201)
    def post(self):
        provider_uuid = get_provider_uuid_from_request()
        collection = request.get_json()
        collection['provider_uuid'] = provider_uuid
        collection = CollectionDB(**collection)
        db.session.add(collection)
        db.session.commit()
        collection = db.session.query(CollectionDB).get(collection.uuid)
        return collection, 201


@ns.route('/<uuid:collection_uuid>')
@ns.response(404, 'Collection not found')
@ns.param('collection_uuid', 'The collection identifier')
class Collection(Resource):
    @jwt_required
    @ns.doc('get_collection')
    @ns.marshal_with(collection_model)
    def get(self, collection_uuid):
        collection = db.session.query(CollectionDB).get(collection_uuid)
        if not collection:
            abort(404)
        return collection

    @jwt_required
    @ns.doc('delete_collection')
    @ns.response(204, 'Collection deleted')
    def delete(self, collection_uuid):
        collection = db.session.query(CollectionDB).filter_by(uuid=collection_uuid).first()
        db.session.delete(collection)
        db.session.commit()
        return '', 204

    @jwt_required
    @ns.doc('update_collection')
    @ns.expect(update_collection_model)
    @ns.marshal_with(collection_model)
    @ns.response(200, 'Collection updated')
    def put(self, collection_uuid):
        collection_dict = request.get_json()
        collection_new = CollectionModel(**collection_dict)

        collection = db.session.query(CollectionDB).get(collection_uuid)

        collection.name = collection_new.name
        collection.is_public = collection_new.is_public

        db.session.commit()
        return collection


@ns.route('/<src_collection_uuid>/copy')
@ns.route('/<src_collection_uuid>/copy/<dst_collection_uuid>')
@ns.param('src_collection_uuid', 'The src collection identifier')
@ns.param('dst_collection_uuid', 'The dst collection identifier')
class CollectionCopy(Resource):
    @jwt_required
    @ns.doc('copy_collection')
    @ns.marshal_with(collection_model, 201)
    def post(src_collection_uuid, dst_collection_uuid=None):
        provider_uuid = get_provider_uuid_from_request()
        try:
            dst_collection_uuid = copy_collection_from(
                src_collection_uuid,
                dst_collection_uuid,
                provider_uuid)
        except PermissionError as e:
            return '', 403

        collection = get_collection_by_uuid(dst_collection_uuid)

        return collection, 201
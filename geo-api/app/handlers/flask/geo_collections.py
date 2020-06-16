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
from flask_accept import accept
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
    'name': fields.String(description='name'),
    'is_public': fields.String(description='is_public'),
})

update_collection_model = api.model('UpdateCollection', {
    'name': fields.String(description='name'),
    'is_public': fields.String(description='is_public'),
})


@ns.route('/')
class CollectionList(Resource):
    @jwt_required
    @ns.doc('list_collections')
    @ns.marshal_list_with(collection_model)
    def get(self):
        provider_uuid = get_provider_uuid_from_request()
        collections = CollectionDB.find_accessible(provider_uuid)
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
        collection.save()
        collection.session().commit()
        return collection, 201


@ns.route('/<uuid:collection_uuid>')
@ns.response(404, 'Collection not found')
@ns.param('collection_uuid', 'The collection identifier')
class Collection(Resource):
    @jwt_required
    @ns.doc('get_collection')
    @ns.marshal_with(collection_model)
    def get(self, collection_uuid):
        provider_uuid = get_provider_uuid_from_request()
        collection = CollectionDB.find_accessible_or_fail(provider_uuid, collection_uuid)
        return collection

    @jwt_required
    @ns.doc('delete_collection')
    @ns.response(204, 'Collection deleted')
    def delete(self, collection_uuid):
        provider_uuid = get_provider_uuid_from_request()
        collection = CollectionDB.first_or_fail(uuid=collection_uuid, provider_uuid=provider_uuid)
        collection.delete()
        collection.session().commit()
        return '', 204

    @jwt_required
    @ns.doc('update_collection')
    @ns.expect(update_collection_model)
    @ns.marshal_with(collection_model)
    @ns.response(200, 'Collection updated')
    def put(self, collection_uuid):
        provider_uuid = get_provider_uuid_from_request()

        collection_dict = request.get_json()
        collection_new = CollectionModel(**collection_dict)

        collection = CollectionDB.first_or_fail(uuid=collection_uuid, provider_uuid=provider_uuid)

        collection.name = collection_new.name
        collection.is_public = collection_new.is_public

        collection.save()
        collection.session().commit()

        return collection


@ns.route('/<uuid:src_collection_uuid>/copy')
@ns.route('/<uuid:src_collection_uuid>/copy/<uuid:dst_collection_uuid>')
@ns.param('src_collection_uuid', 'The src collection identifier')
@ns.param('dst_collection_uuid', 'The dst collection identifier')
class CollectionCopy(Resource):
    @jwt_required
    @ns.doc('copy_collection')
    @ns.marshal_with(collection_model, 201)
    def post(self, src_collection_uuid, dst_collection_uuid=None):
        provider_uuid = get_provider_uuid_from_request()
        try:
            dst_collection_uuid = copy_collection_from(
                src_collection_uuid,
                dst_collection_uuid,
                provider_uuid)
        except PermissionError as e:
            return '', 403

        collection = CollectionDB.find_or_fail(dst_collection_uuid)

        return collection, 201

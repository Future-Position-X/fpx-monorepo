import rapidjson
from app import app, api
from flask_restx import Resource, fields
from app.models.collection import Collection
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

ns = api.namespace('collections', 'Collection operations')

collection = api.model('Collection', {
    'uuid': fields.String(description='uuid'),
    'provider_uuid': fields.String(description='provider_uuid'),
    'name': fields.String(description='name'),
    'is_public': fields.String(description='is_public'),
    'revision': fields.String(description='revision'),
    'created_at': fields.String(description='created_at'),
    'updated_at': fields.String(description='updated_at'),
})

create_collection = api.model('CreateCollection', {
    'provider_uuid': fields.String(description='provider_uuid'),
    'name': fields.String(description='name'),
    'is_public': fields.String(description='is_public'),
})

update_collection = api.model('UpdateCollection', {
    'provider_uuid': fields.String(description='provider_uuid'),
    'name': fields.String(description='name'),
    'is_public': fields.String(description='is_public'),
})

@ns.route('/')
class CollectionList(Resource):
    @jwt_required
    @ns.doc('list_collections')
    @ns.marshal_list_with(collection)
    def get(self):
        collections = get_all_collections()
        # return response(200, rapidjson.dumps([c.as_dict() for c in collections], datetime_mode=DM_ISO8601))
        return collections

    @jwt_required
    @ns.doc('create_collection')
    @ns.expect(create_collection)
    @ns.marshal_with(collection, 201)
    def post(self):
        provider_uuid = get_provider_uuid_from_request()
        payload = api.playload
        collection = rapidjson.loads(payload)
        collection['provider_uuid'] = provider_uuid
        collection = Collection(**collection)
        uuid = create_collection(collection)
        collection = get_collection_by_uuid(uuid)
        # return response(201, uuid)
        return collection


@ns.route('/<uuid:collection_uuid>')
@ns.response(404, 'Collection not found')
@ns.param('collection_uuid', 'The collection identifier')
class Collection(Resource):
    @jwt_required
    @ns.doc('get_collection')
    @ns.marshal_with(collection)
    def get(self, collection_uuid):
        collection = get_collection_by_uuid(collection_uuid)

        return collection

    @jwt_required
    @ns.doc('delete_collection')
    @ns.response(204, 'Collection deleted')
    def delete(self, collection_uuid):
        delete_collection_by_uuid(collection_uuid)

        return '', 204

    @jwt_required
    @ns.doc('update_collection')
    @ns.expect(update_collection)
    @ns.marshal_with(collection)
    @ns.response(200, 'Collection updated')
    def put(self, collection_uuid):
        payload = api.playload
        collection_dict = rapidjson.loads(payload)
        collection = Collection(**collection_dict)
        update_collection_by_uuid(collection_uuid, collection)
        collection = get_collection_by_uuid(collection_uuid)

        return collection


@ns.route('/<src_collection_uuid>/copy')
@ns.route('/<src_collection_uuid>/copy/<dst_collection_uuid>')
@ns.param('src_collection_uuid', 'The src collection identifier')
@ns.param('dst_collection_uuid', 'The dst collection identifier')
class CollectionCopy(Resource):
    @jwt_required
    @ns.doc('copy_collection')
    @ns.marshal_with(collection, 201)
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

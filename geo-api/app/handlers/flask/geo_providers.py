from flask_restx import Resource, fields
from app import api
from app.models.provider import Provider
from app.models import Provider as ProviderDB
from app.handlers.flask import (
    get_provider_uuid_from_request
)
from flask import request
from flask_jwt_extended import jwt_required

ns = api.namespace('providers', 'Provider operations')

provider_model = api.model('Provider', {
    'uuid': fields.String(description='uuid'),
    'name': fields.String(description='name'),
    'revision': fields.String(description='revision'),
    'created_at': fields.String(description='created_at'),
    'updated_at': fields.String(description='updated_at'),
})
update_provider_model = api.model('UpdateProvider', {
    'name': fields.String(description='name'),
})


@ns.route('/')
class ProviderList(Resource):
    @ns.doc('list_providers', security=None)
    @ns.marshal_list_with(provider_model)
    def get(self):
        providers = ProviderDB.all()
        return providers


@ns.route('/<uuid:provider_uuid>')
@ns.response(404, 'Provider not found')
@ns.param('provider_uuid', 'The provider identifier')
class ProviderApi(Resource):
    @ns.doc('get_provider', security=None)
    @ns.marshal_with(provider_model)
    def get(self, provider_uuid):
        provider = ProviderDB.find_or_fail(provider_uuid)
        return provider

    @jwt_required
    @ns.doc('update_provider')
    @ns.expect(update_provider_model)
    def put(self, provider_uuid):
        if get_provider_uuid_from_request() != provider_uuid:
            return '', 403
        provider_dict = request.get_json()
        provider_new = Provider(**provider_dict)
        provider = ProviderDB.find_or_fail(provider_uuid)
        provider.name = provider_new.name
        provider.save()
        provider.session().commit()
        return '', 204

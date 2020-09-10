from flask import request
from flask_jwt_extended import jwt_required
from flask_restx import Resource, fields

from app import api
from app.dto import ACLDTO
from app.handlers.flask import get_user_from_request
from app.services.acl import (
    get_all_readable_acls,
    create_acl,
    get_acl_by_uuid,
    delete_acl_by_uuid,
)

ns = api.namespace("acls", "ACL operations")

acl_model = api.model(
    "ACL",
    {
        "uuid": fields.String(description="uuid"),
        "provider_uuid": fields.String(description="provider_uuid"),
        "granted_provider_uuid": fields.String(description="granted_provider_uuid"),
        "granted_user_uuid": fields.String(description="granted_user_uuid"),
        "collection_uuid": fields.String(description="collection_uuid"),
        "item_uuid": fields.String(description="item_uuid"),
        "access": fields.String(description="access, read|write"),
        "revision": fields.Integer(description="revision"),
        "created_at": fields.String(description="created_at"),
        "updated_at": fields.String(description="updated_at"),
    },
)

create_acl_model = api.model(
    "CreateACL",
    {
        "granted_provider_uuid": fields.String(description="granted_provider_uuid"),
        "granted_user_uuid": fields.String(description="granted_user_uuid"),
        "collection_uuid": fields.String(description="collection_uuid"),
        "item_uuid": fields.String(description="item_uuid"),
        "access": fields.String(description="access, read|write"),
    },
)


@ns.route("/")
class ACLListApi(Resource):
    @jwt_required
    @ns.doc("list_acls")
    @ns.marshal_list_with(acl_model)
    def get(self):
        user = get_user_from_request()
        acls = get_all_readable_acls(user)
        return acls

    @jwt_required
    @ns.doc("create_collection")
    @ns.expect(create_acl_model)
    @ns.marshal_with(acl_model, code=201)
    def post(self):
        user = get_user_from_request()
        acl = ACLDTO(**request.get_json())

        # Check valid request
        if not (
            bool(acl.granted_provider_uuid) != bool(acl.granted_user_uuid)
            and bool(acl.collection_uuid) != bool(acl.item_uuid)
            and acl.access in ["read", "write"]
        ):
            raise ValueError

        acl = create_acl(user, acl)
        return acl, 201


@ns.route("/<uuid:acl_uuid>")
@ns.response(404, "ACL not found")
@ns.param("acl_uuid", "The ACL identifier")
class ACLApi(Resource):
    @jwt_required
    @ns.doc("get_acl")
    @ns.marshal_with(acl_model)
    def get(self, acl_uuid):
        user = get_user_from_request()
        acl = get_acl_by_uuid(user, acl_uuid)
        return acl

    @jwt_required
    @ns.doc("delete_acl")
    @ns.response(204, "ACL deleted")
    def delete(self, acl_uuid):
        user = get_user_from_request()
        delete_acl_by_uuid(user, acl_uuid)
        return "", 204

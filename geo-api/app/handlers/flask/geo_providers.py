import rapidjson
import base64
from rapidjson import DM_ISO8601, UM_CANONICAL

from app import app
from app.models.provider import Provider
from app.handlers.flask import (
    response,
    get_provider_uuid_from_request
)
from app.services.provider import (
    get_provider_by_uuid,
    get_all_providers,
    update_provider_by_uuid,
    )
from flask import request
from flask_jwt_extended import jwt_required


@app.route('/providers')
@jwt_required
def providers_index():
    providers = get_all_providers()

    return response(200, rapidjson.dumps([p.as_dict() for p in providers], datetime_mode=DM_ISO8601, uuid_mode=UM_CANONICAL))


@app.route('/providers/<provier_uuid>')
@jwt_required
def providers_get(provider_uuid):
    provider = get_provider_by_uuid(provider_uuid)
    return response(200, rapidjson.dumps(provider.as_dict(), datetime_mode=DM_ISO8601))


@app.route('/providers/<provider_uuid>', methods=['PUT'])
@jwt_required
def providers_update(provider_uuid):
    provider_dict = request.json
    provider = Provider(**provider_dict)
    update_provider_by_uuid(provider_uuid, provider)
    return response(204)

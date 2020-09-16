import os
from flask import Flask
from flask_restx import Api, ValidationError
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import sqlalchemy_mixins
from app.config import app_config

api = Api(
    authorizations={
        "apikey": {"type": "apiKey", "in": "header", "name": "authorization"}
    },
    security="apikey",
)
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
app = None


def create_app(config_name=None):
    app = Flask(__name__)
    CORS(app)
    if config_name is None:
        config_name = os.environ.get("APP_SETTINGS", "development")
    app.config.from_object(app_config[config_name])
    app.url_map.strict_slashes = False
    api.init_app(
        app,
        version="1.0",
        title="GIA geo api",
        description="GIA geo api",
        contact="Magnus Engström",
        contact_url="http://fpx.se",
        contact_email="magnus.engstrom@fpx.se",
    )
    db.init_app(app)

    # This does not migrate or update the DB, you need to run $flask db upgrade
    migrate.init_app(app, db)

    jwt.init_app(app)

    from app.models import BaseModel

    BaseModel.set_session(db.session)

    from app.handlers.flask import (
        handle_model_not_found_error,
        handle_permission_error,
        handle_value_error,
        handle_validation_error,
    )

    app.register_error_handler(
        sqlalchemy_mixins.ModelNotFoundError, handle_model_not_found_error
    )
    app.register_error_handler(PermissionError, handle_permission_error)
    app.register_error_handler(ValidationError, handle_validation_error)
    app.register_error_handler(ValueError, handle_value_error)

    from app.handlers.flask import (  # noqa:
        geo_acls,
        geo_collections,
        geo_items,
        geo_sessions,
        geo_users,
        geo_providers,
        handler,
    )

    return app


def create_app_for_console(config_name=None):
    cli_app = create_app(config_name)
    cli_app.app_context().push()
    return cli_app

import os
from flask import Flask
from flask_restx import Api
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sqlalchemy_mixins

from app.config import app_config
api = Api()
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
app = None


def create_app(config_name=None):
    app = Flask(__name__)
    if config_name == None:
        config_name = os.environ.get('APP_SETTINGS', 'development')
    app.config.from_object(app_config[config_name])
    app.url_map.strict_slashes = False
    api.init_app(app, version='1.0', title='GIA geo api',
                 description='GIA geo api',
                 contact='Magnus Engström',
                 contact_url='http://fpx.se',
                 contact_email='magnus.engstrom@fpx.se'
                 )
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from app.models import BaseModel2
    BaseModel2.set_session(db.session)

    from app.handlers.flask import handle_model_not_found_error
    app.register_error_handler(sqlalchemy_mixins.ModelNotFoundError, handle_model_not_found_error)

    from app.handlers.flask import geo_collections, geo_items, geo_sessions, geo_users, geo_providers, handler

    return app

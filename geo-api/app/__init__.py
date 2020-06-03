import os
from flask import Flask
from flask_jwt_extended import JWTManager
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET')
app.config['JWT_IDENTITY_CLAIM'] = 'sub'
jwt = JWTManager(app)
from app.handlers.flask import geo_collections, geo_items, geo_providers, handler

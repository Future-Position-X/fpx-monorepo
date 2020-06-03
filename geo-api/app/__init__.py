import os
from flask import Flask
from flask_restx import Api
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.url_map.strict_slashes = False
api = Api(app, version='1.0', title='GIA geo api',
          description='GIA geo api',
          contact='Magnus Engström',
          contact_url='http://fpx.se',
          contact_email='magnus.engstrom@fpx.se'
          )
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET')
app.config['JWT_IDENTITY_CLAIM'] = 'sub'
jwt = JWTManager(app)
from app.handlers.flask import geo_collections, geo_items, geo_providers, geo_sessions, geo_users, handler

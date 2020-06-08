import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = os.environ.get('JWT_SECRET', 'mRJZQrLE6HlStXd4eEQcMLNDDIltgo1eYUzA5TbAcaRlwCX6FI2SLYKjgq19')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://master:master@localhost:5432/development')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_IDENTITY_CLAIM = 'sub'


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://master:master@localhost:5432/testing'
    SQLALCHEMY_ECHO = True

app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
}
